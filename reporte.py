# reporte.py

import os
import time

ruta_reporte = None  # Ruta al archivo .txt donde se va armando el reporte
nombre_archivo_excel = None

def inicializar_reporte(nombre_archivo, ruta_guardado):
    global ruta_reporte, nombre_archivo_excel
    nombre_archivo_excel = nombre_archivo
    ruta_reporte = os.path.join(ruta_guardado, "reporte_diagnostico.txt")
    os.makedirs(ruta_guardado, exist_ok=True)

    with open(ruta_reporte, "w", encoding="utf-8") as f:
        f.write("DIAGNÓSTICO DE CATÁLOGO - REPORTE GENERAL\n")
        f.write("=" * 50 + "\n")
        f.write(f"Archivo analizado: {nombre_archivo}\n\n")

def agregar_etapa_limpieza(filas_antes, filas_despues, columnas, duracion, nulos_por_columna):
    porcentaje_eliminadas = ((filas_antes - filas_despues) / filas_antes) * 100 if filas_antes else 0
    with open(ruta_reporte, "a", encoding="utf-8") as f:
        f.write("[ ETAPA 1 - LIMPIEZA DE DATOS ]\n")
        f.write(f"Tiempo de limpieza: {duracion:.2f} segundos\n")
        f.write(f"Filas antes de limpiar: {filas_antes}\n")
        f.write(f"Filas después de limpiar: {filas_despues}\n")
        f.write(f"Filas eliminadas: {filas_antes - filas_despues}\n")
        f.write(f"Columnas actuales: {columnas}\n")
        f.write("Porcentaje de valores nulos por columna:\n")
        for col, val in nulos_por_columna.items():
            f.write(f"  - {col}: {val:.2f}%\n")
        f.write("\n")

def agregar_etapa_graficos(tiempo_graficos, graficos_ok, graficos_fallidos):
    with open(ruta_reporte, "a", encoding="utf-8") as f:
        f.write("[ ETAPA 2 - GENERACIÓN DE GRÁFICOS ]\n")
        f.write(f"Tiempo total de generación de gráficos: {tiempo_graficos:.2f} segundos\n\n")

        f.write("Gráficos generados exitosamente:\n")
        if graficos_ok:
            for nombre in graficos_ok:
                f.write(f"  ✔ {nombre}\n")
        else:
            f.write("  (Ninguno)\n")

        f.write("\nGráficos omitidos por falta de datos:\n")
        if graficos_fallidos:
            for nombre in graficos_fallidos:
                f.write(f"  ⚠ {nombre}\n")
        else:
            f.write("  (Ninguno)\n")
        f.write("\n")

def agregar_etapa_general(filas, columnas, duracion_total):
    with open(ruta_reporte, "a", encoding="utf-8") as f:
        f.write("[ ETAPA 3 - INFORMACIÓN GENERAL ]\n")
        f.write(f"Filas totales: {filas}\n")
        f.write(f"Columnas totales: {columnas}\n")
        f.write(f"Tiempo total de procesamiento: {duracion_total:.2f} segundos\n")
        f.write("\n" + "=" * 50 + "\n")
        f.write("Fin del reporte.\n")
