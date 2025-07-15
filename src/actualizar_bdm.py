# actualizar_bdm.py

import os
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError

# ⚙️ Parámetros de conexión
usuario = "root"
contraseña = "Sql150796*"
host = "127.0.0.1"
puerto = 3306
base_datos = "base_datos_maestra"

# 📦 Crear motor de conexión
engine = create_engine(
    f"mysql+pymysql://{usuario}:{contraseña}@{host}:{puerto}/{base_datos}"
)

def actualizar_bdm(
    ruta_catalogo: str,
    ruta_codigos: str,
    ruta_mapeos: str,
    ruta_caracteristicas: str
) -> None:
    """
    Inserta en la BDM los registros nuevos del catálogo procesado.
    """
    # — Leer catálogo final —
    if not os.path.exists(ruta_catalogo):
        print(f"❌ No se encontró el archivo de catálogo: {ruta_catalogo}")
        return

    df_catalogo = pd.read_csv(ruta_catalogo)

    # — Hashes únicos en el catálogo —
    hashes_nuevos = set(df_catalogo["description_hash"].unique())

    # — Leer hashes existentes en la BDM —
    try:
        df_existentes = pd.read_sql(
            "SELECT description_hash FROM validated_materials",
            con=engine
        )
        hashes_existentes = set(df_existentes["description_hash"].unique())
    except Exception:
        hashes_existentes = set()

    # — Filtrar solo registros nuevos —
    df_nuevos = df_catalogo[
        ~df_catalogo["description_hash"].isin(hashes_existentes)
    ].copy()
    print(f"🆕 Nuevos materiales para insertar: {len(df_nuevos)}")

    if df_nuevos.empty:
        print("ℹ️ No hay registros nuevos para insertar.")
        return

    # — Preparar DataFrames para cada tabla —
    cols_materials = ["description_hash", "description_final", "grupo", "producto", "codigo"]
    df_materials = df_nuevos[cols_materials].drop_duplicates()

    cols_caracteristicas = ["description_hash", "name", "value", "hierarchy_level"]
    df_characteristics = df_nuevos[cols_caracteristicas].drop_duplicates()

    # — Insertar en la BDM —
    try:
        df_materials.to_sql(
            "validated_materials",
            con=engine,
            if_exists="append",
            index=False
        )
        df_characteristics.to_sql(
            "validated_characteristics",
            con=engine,
            if_exists="append",
            index=False
        )
        print("✅ Nuevos datos insertados en la BDM correctamente.")
    except IntegrityError as e:
        print("❌ Error de integridad al insertar:")
        print(e)
    except Exception as e:
        print("❌ Otro error al insertar:")
        print(e)
