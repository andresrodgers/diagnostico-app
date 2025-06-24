# src/cargar_datos_spark.py
import pandas as pd
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, trim
import os
from datetime import datetime

# Columnas críticas que deben existir
COLUMNAS_CRITICAS = [
    "Cod. Prod. V14", "Nombre Producto V4",
    "Cod. Prod. V26 ES", "Nombre Producto V26 ES",
    "plantilla_final"
]

# Mapeo estándar
MAPPING_COLUMNAS = {
    "Cod. Prod. V14": "codigo_v14",
    "Nombre Producto V4": "nombre_v14",
    "Cod. Prod. V26 ES": "codigo_v26",
    "Nombre Producto V26 ES": "nombre_v26",
    "plantilla_final": "plantilla"
}

def cargar_y_limpiar_datos_spark(spark: SparkSession, ruta_excel: str):
    # Leer con pandas y validar columnas
    df_pandas = pd.read_excel(ruta_excel, dtype=str)
    
    faltantes = [col for col in COLUMNAS_CRITICAS if col not in df_pandas.columns]
    if faltantes:
        raise ValueError(f"❌ Columnas faltantes en el archivo: {faltantes}")

    # Renombrar columnas clave
    df_pandas = df_pandas.rename(columns=MAPPING_COLUMNAS)

    # Limpieza básica: eliminar .0 y espacios
    for col_code in ["codigo_v14", "codigo_v26"]:
        df_pandas[col_code] = df_pandas[col_code].str.replace(".0", "", regex=False).str.strip()

    # Eliminar filas totalmente vacías
    df_pandas.dropna(how="all", inplace=True)

    # Filtrar las que tengan características
    df_filtrado = df_pandas[df_pandas["plantilla"].notna()].copy()

    # Completar campos finales
    df_filtrado["codigo_final"] = df_filtrado["codigo_v26"].fillna(df_filtrado["codigo_v14"])
    df_filtrado["nombre_final"] = df_filtrado["nombre_v26"].fillna(df_filtrado["nombre_v14"])

    # Convertir a Spark
    df_spark = spark.createDataFrame(df_filtrado)

    # Trim a todo para limpieza general
    for col_name in df_spark.columns:
        df_spark = df_spark.withColumn(col_name, trim(col(col_name)))

    # Guardar reporte de limpieza
    guardar_reporte_limpieza(df_filtrado)

    return df_spark

def guardar_reporte_limpieza(df_pandas):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    ruta = f"data/processed/reporte_limpieza_{timestamp}.txt"
    os.makedirs("data/processed", exist_ok=True)

    with open(ruta, "w", encoding="utf-8") as f:
        f.write("📋 REPORTE DE LIMPIEZA\n")
        f.write(f"Total filas: {len(df_pandas)}\n")
        f.write(f"Filas con plantilla: {df_pandas['plantilla'].notna().sum()}\n")
        f.write(f"Códigos únicos V14: {df_pandas['codigo_v14'].nunique()}\n")
        f.write(f"Códigos únicos V26: {df_pandas['codigo_v26'].nunique()}\n")
        f.write(f"Códigos finales únicos: {df_pandas['codigo_v26'].fillna(df_pandas['codigo_v14']).nunique()}\n")

    print(f"✅ Reporte de limpieza generado: {ruta}")