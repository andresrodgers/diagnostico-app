# cargar_datos.py
import pandas as pd
import numpy as np
import unicodedata
import re
import time
from reporte import agregar_etapa_limpieza
from langdetect import detect, DetectorFactory
from src.cargar_datos_spark import cargar_y_limpiar_datos_spark


# --- Normalización del encabezado ---
def normalizar_texto_encabezado(texto):
    if not isinstance(texto, str):
        return ""
    texto = texto.lower()
    texto = unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode()
    texto = re.sub(r"[^a-z0-9 ]", " ", texto)
    texto = re.sub(r"\s+", " ", texto)
    texto = texto.strip()
    return texto

# --- Normalización de los datos ---
def limpiar_valores_df(df):
    def limpiar_valor(val):
        if isinstance(val, str):
            val = unicodedata.normalize('NFKD', val).encode('ASCII', 'ignore').decode()
            val = val.replace('\u200b', '').replace('"', '').replace("—", "-")
            val = val.strip().lower()
            val = re.sub(r"\s+", " ", val)
        return val
    return df.map(limpiar_valor)

# --- Mapeo flexible de columnas ---
MAPPING_COLUMNAS = {
    "Descripcion Corta": ["descripcion de articulo corta", "desc corta", "descripcion corta"],
    "Descripcion Larga": ["descripcion de articulo larga", "desc larga", "descripcion larga"],
    "Codigo material": ["codigo del material", "codigo", "codigo material"],
    "Unidad de medida": ["unidad de medida principal", "unidad de medida"],
    "Grupo Unspsc": ["grupo norma - unspsc", "grupo"],
    "Producto Unspsc": ["producto - unspsc", "producto", "producto unspsc"],
    "Codigo de Categoria": ["codigo de categoria", "cod tipo material"],
    "Tipo de articulo": ["tipo de articulo", "articulo - tipo de articulo de usuario", "tipo"]
}

def mapear_columnas_similares(columnas):
    columnas_normalizadas = {normalizar_texto_encabezado(c): c for c in columnas}
    nuevo_nombre = {}
    for estandar, variantes in MAPPING_COLUMNAS.items():
        nombres_posibles = [normalizar_texto_encabezado(v) for v in variantes + [estandar]]
        for nombre in nombres_posibles:
            if nombre in columnas_normalizadas:
                original = columnas_normalizadas[nombre]
                nuevo_nombre[original] = estandar
                break
    return nuevo_nombre

# --- Cargar, limpiar y validar datos ---
def cargar_y_limpiar_datos(path_excel, ruta_guardado, barra_progreso=None, ventana=None):

    inicio = time.time()
    df_original = pd.read_excel(path_excel, dtype=str)

    if barra_progreso:
        barra_progreso.set(0.1)
        ventana.update_idletasks()

    filas_antes = len(df_original)
    columnas_antes = len(df_original.columns)

    # Normalizar encabezados y renombrar
    columnas_mapeadas = mapear_columnas_similares(df_original.columns)
    df_original.rename(columns=columnas_mapeadas, inplace=True)

    if barra_progreso:
        barra_progreso.set(0.2)  # Luego de renombrar columnas
        ventana.update_idletasks()

    # Eliminar filas completamente vacías
    df_original.dropna(how="all", inplace=True)

    # Limpiar valores
    df = limpiar_valores_df(df_original)

    # --- Unificar separadores en descripciones ---
    def unificar_separadores(texto):
        if not isinstance(texto, str):
            return texto
        texto = re.sub(r"[;,/\\\-]+", ",", texto)  # Reemplaza por coma
        texto = re.sub(r"\s*,\s*", ",", texto)     # Limpia espacios alrededor de comas
        return texto.strip(",")

    for col in ["Descripcion Corta", "Descripcion Larga"]:
        if col in df.columns:
            df[col] = df[col].apply(unificar_separadores)


    DetectorFactory.seed = 0
    def detectar_idioma(texto):
        if pd.isna(texto) or texto == "":
            return 'Nulo/Vacío'
        try:
            idioma = detect(texto)
            if idioma == 'es':
                return 'Español'
            elif idioma == 'en':
                return 'Inglés'
            else:
                return 'Mezcla'
        except:
            return 'Mezcla'

    if barra_progreso:
        barra_progreso.set(0.25)  # Luego de eliminar filas vacías
        ventana.update_idletasks()

    # Detectar idioma en columna 'Descripcion Larga'
    if "Descripcion Larga" in df.columns:
        total = len(df)
        progreso_base = 0.25
        progreso_final = 0.7
        pasos = 21
        incremento = (progreso_final - progreso_base) / pasos
        filas_por_paso = total // pasos
        idiomas = []
        paso_actual = 0

        for idx, texto in enumerate(df["Descripcion Larga"]):
            idiomas.append(detectar_idioma(texto))

            if barra_progreso and (idx + 1) >= (paso_actual + 1) * filas_por_paso:
                paso_actual += 1
                nuevo_valor = progreso_base + paso_actual * incremento
                barra_progreso.set(min(nuevo_valor, progreso_final))
                ventana.update_idletasks()

        df["Idioma"] = idiomas

    # Validación de columnas críticas
    columnas_requeridas = ["Descripcion Larga", "Producto Unspsc", "Descripcion Corta"]
    faltantes = [col for col in columnas_requeridas if col not in df.columns]
    if faltantes:
        raise ValueError(f"Faltan columnas críticas: {', '.join(faltantes)}")

    filas_despues = len(df)
    columnas_final = len(df.columns)

    # Porcentaje de nulos por columna
    nulos_por_columna = (df.isnull().sum() / len(df)) * 100

    # Registrar en reporte
    agregar_etapa_limpieza(
        filas_antes=filas_antes,
        filas_despues=filas_despues,
        columnas=columnas_final,
        duracion=time.time() - inicio,
        nulos_por_columna=nulos_por_columna
    )

    # Empaquetar información de limpieza para diagnostico.py
    info_limpieza = {
        "filas_antes": filas_antes,
        "filas_despues": filas_despues,
        "columnas": columnas_final,
        "nulos_por_columna": nulos_por_columna
    }

    return df, info_limpieza 

