# graficos.py

import os
import matplotlib.pyplot as plt
import seaborn as sns
import textwrap
import pandas as pd
import numpy as np
from utils.helpers import extraer_caracteristicas
from utils.helpers import extraer_producto_unspc, extraer_primera_parte_desc_larga

import matplotlib.pyplot as plt

def dibujar_etiquetas_pie(fig, ax, etiquetas, valores, colores, titulo, total=None):
    """
    Dibuja gráfico de pastel con:
    - Etiquetas a la derecha, centradas verticalmente respecto al gráfico.
    - Título centrado respecto al conjunto (gráfico + etiquetas).
    """
    wedges, _ = ax.pie(valores, startangle=90, colors=colores, wedgeprops={'edgecolor': 'black'}, labels=None)

    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    bbox_ax = ax.get_window_extent(renderer=renderer)

    # Centro vertical del gráfico (en coords figura)
    fig_height_px = fig.get_size_inches()[1] * fig.dpi
    centro_y = (bbox_ax.y0 + bbox_ax.y1) / 2 / fig_height_px

    # Coordenadas Y para etiquetas
    espacio_y = 0.05
    y_inicio = centro_y + espacio_y * (len(etiquetas) - 1) / 2

    # Posición horizontal fija a la derecha del gráfico
    x_texto = 0.95
    x_circulo = 0.90

    total_val = total if total is not None else sum(valores)

    for i, valor in enumerate(valores):
        y_pos = y_inicio - i * espacio_y
        porcentaje = (valor / total_val) * 100
        texto = f"{etiquetas[i]}: {valor} ({porcentaje:.2f}%)"
        fig.text(x_texto, y_pos, texto, fontsize=10, ha='left', va='center')
        ax.scatter(x_circulo, y_pos, s=100, color=colores[i], edgecolor='black', transform=fig.transFigure, clip_on=False)

    fig.suptitle(titulo, fontsize=12, ha='center', y=0.95)
    ax.set_aspect('equal')
    plt.tight_layout()

# Ajusta etiquetas largas dividiéndolas en varias líneas
def wrap_labels(labels, width=30):
    return ['\n'.join(textwrap.wrap(l, width)) for l in labels]

# Guarda una figura en la carpeta indicada
def guardar_grafico(fig, nombre, ruta):
    fig.savefig(os.path.join(ruta, f"{nombre}.png"), bbox_inches='tight')
    plt.close(fig)

def graficar_porcentaje_datos(df, ruta_guardado):
    """
    Genera gráfico de barras con el porcentaje de datos presentes por columna.
    Guarda el gráfico como 'Porcentaje_datos.png' en la carpeta indicada.
    """
    total_filas = len(df)
    porcentaje_datos = (df.notnull().sum() / total_filas) * 100
    colores = plt.cm.Paired(range(len(porcentaje_datos)))

    plt.figure(figsize=(12, 5))
    ax = sns.barplot(x=porcentaje_datos.index, y=porcentaje_datos.values, palette=colores, edgecolor='black')

    for i, v in enumerate(porcentaje_datos.values):
        ax.text(i, v + 1, f"{v:.1f}%", ha="center", fontsize=7, fontweight="bold")

    plt.xticks(rotation=90)
    plt.ylabel("Porcentaje de datos %")
    plt.title("Porcentaje de datos presentes en cada columna")
    plt.ylim(0, 110)
    plt.tight_layout()

    guardar_grafico(plt.gcf(), "1. Porcentaje datos", os.path.join(ruta_guardado, "graficos"))

def graficar_descripciones_unicas(df, ruta_guardado):
    """
    Genera gráfico de barras con cantidad estimada de descripciones únicas
    en columnas corta y larga, considerando elementos ordenados por comas.
    """
    total_filas = len(df)

    # Crear columnas ordenadas
    df["_desc_larga_ordenada"] = df["Descripcion Larga"].astype(str).apply(lambda x: ",".join(sorted(x.split(","))))
    df["_desc_corta_ordenada"] = df["Descripcion Corta"].astype(str).apply(lambda x: ",".join(sorted(x.split(","))))

    # Identificar duplicados
    dup_larga = df["_desc_larga_ordenada"].duplicated(keep=False)
    dup_corta = df["_desc_corta_ordenada"].duplicated(keep=False)

    sin_dup_larga = df[~dup_larga]["_desc_larga_ordenada"]
    sin_dup_corta = df[~dup_corta]["_desc_corta_ordenada"]

    val_unicos_larga = sin_dup_larga.nunique()
    val_unicos_corta = sin_dup_corta.nunique()

    dup_larga_count = dup_larga.sum()
    dup_corta_count = dup_corta.sum()

    val_unicos_larga_fin = val_unicos_larga + (dup_larga_count / 2)
    val_unicos_corta_fin = val_unicos_corta + (dup_corta_count / 2)

    etiquetas = ["Descripcion corta", "Descripcion larga"]
    valores = [val_unicos_corta_fin, val_unicos_larga_fin]
    colores = plt.cm.Paired(range(len(valores)))

    fig, ax = plt.subplots(figsize=(5, 5))
    ax.bar(etiquetas, valores, color=colores, edgecolor='black')

    for i, valor in enumerate(valores):
        pct = (valor / total_filas) * 100
        ax.text(i, valor + 100, f"{int(valor)} ({pct:.2f}%)", ha='center', fontsize=10, fontweight='bold')

    ax.set_ylabel("Cantidad de valores únicos")
    ax.set_title(f"Descripciones únicas (Total filas: {total_filas})")
    ax.set_ylim(0, total_filas * 1.05)
    plt.tight_layout()

    guardar_grafico(fig, "2. Descripciones unicas", os.path.join(ruta_guardado, "graficos"))

def graficar_duplicados_descripciones(df, ruta_guardado):
    """
    Genera gráfico de pastel con duplicados en descripciones corta y larga,
    considerando descripciones con mismos elementos separados por comas aunque en diferente orden.
    """
    #    # Generar columnas ordenadas alfabéticamente
    df["_desc_larga_ordenada"] = df["Descripcion Larga"].astype(str).apply(lambda x: ",".join(sorted(x.split(","))))
    df["_desc_corta_ordenada"] = df["Descripcion Corta"].astype(str).apply(lambda x: ",".join(sorted(x.split(","))))

    # Total por cada tipo
    total_larga = df["_desc_larga_ordenada"].shape[0]
    total_corta = df["_desc_corta_ordenada"].shape[0]

    # Identificar duplicados (contar pares únicos)
    dup_larga_count = df["_desc_larga_ordenada"].duplicated(keep=False).sum() // 2
    dup_corta_count = df["_desc_corta_ordenada"].duplicated(keep=False).sum() // 2

    valores = [dup_corta_count, dup_larga_count]
    total_filas = len(df)

    etiquetas = ["Corta","Larga"]

    colores = plt.cm.Paired(range(len(valores)))

    fig, ax = plt.subplots(figsize=(6, 5))
    dibujar_etiquetas_pie(
        fig, ax,
        etiquetas=etiquetas,
        valores=valores,
        colores=colores,
        titulo="Duplicados en Descripciones",
        total=total_filas
    )

    plt.axis('equal')
    plt.tight_layout()
    guardar_grafico(fig, "3. Descripciones duplicadas", os.path.join(ruta_guardado, "graficos"))

def graficar_falta_info_descripcion_corta(df, ruta_guardado):
    """
    Genera gráfico de pastel mostrando si las descripciones cortas tienen más de 20 caracteres,
    20 o menos, o si están vacías/nulas.
    Guarda el gráfico como 'Falta_informacion.png'.
    """
    df["Total caracteres"] = df["Descripcion Corta"].astype(str).str.len()

    mas_20 = (df["Total caracteres"] > 20).sum()
    menos_igual_20 = (df["Total caracteres"] <= 20).sum()
    nulos_o_vacios = df["Descripcion Corta"].isnull().sum() + (df["Descripcion Corta"] == "").sum()

    etiquetas = ["Más de 20", "20 o menos", "Nulos/vacíos"]
    valores = [mas_20, menos_igual_20, nulos_o_vacios]
    colores = plt.cm.Paired(range(len(valores)))

    fig, ax = plt.subplots(figsize=(6, 5))
    dibujar_etiquetas_pie(
        fig, ax,
        etiquetas=["Más de 20", "20 o menos", "Nulos/vacíos"],
        valores=valores,
        colores=colores,
        titulo="Falta de información: Descripción Corta"
    )

    plt.axis('equal')
    plt.tight_layout()

    guardar_grafico(fig, "4. Falta informacion", os.path.join(ruta_guardado, "graficos"))

def graficar_idiomas_descripcion_larga(df, ruta_guardado):
    """
    Genera gráfico de pastel mostrando la distribución de idiomas detectados
    en la descripción larga. Guarda el gráfico como 'Desc_idioma.png'.
    """
    idiomas_count = df["Idioma"].value_counts()
    etiquetas = idiomas_count.index.tolist()
    valores = idiomas_count.values.tolist()
    colores = plt.cm.Paired(range(len(valores)))

    fig, ax = plt.subplots(figsize=(6, 5))
    dibujar_etiquetas_pie(
        fig, ax,
        etiquetas=etiquetas,
        valores=valores,
        colores=colores,
        titulo="Distribución de Idiomas: Descripción larga"
    )

    plt.axis('equal')
    plt.tight_layout()

    guardar_grafico(fig, "5. Distribucion de idioma", os.path.join(ruta_guardado, "graficos"))

def graficar_unidades_medida(df, ruta_guardado):
    """
    Genera gráfico de pastel con la distribución de valores en 'Unidad de medida',
    incluyendo valores nulos. Guarda el gráfico como 'Unidades_medida.png'.
    """
    valores_unicos = df['Unidad de medida'].value_counts(dropna=False)
    nulos = valores_unicos.get(np.nan, 0)
    valores_unicos = valores_unicos.dropna()

    etiquetas = list(valores_unicos.index) + ["Nulos"]
    totales = list(valores_unicos.values) + [nulos]
    colores = plt.cm.Paired(range(len(totales)))

    fig, ax = plt.subplots(figsize=(6, 5))
    dibujar_etiquetas_pie(
        fig, ax,
        etiquetas=etiquetas,
        valores=totales,
        colores=colores,
        titulo=f"Distribución de valores en Unidad de medida"
    )

    plt.axis('equal')
    plt.tight_layout()

    guardar_grafico(fig, "6. Unidades medida", os.path.join(ruta_guardado, "graficos"))

def graficar_top_grupo_unspsc(df, ruta_guardado):
    """
    Genera gráfico de barras horizontales con el Top 10 de Grupo UNSPSC + 'Otros'.
    Guarda el gráfico como 'Grupo_UNSPSC.png'.
    """
    grupo_counts = df["Grupo Unspsc"].value_counts(dropna=False)
    top_10 = grupo_counts.head(10)
    otros = grupo_counts.iloc[10:].sum()

    if otros > 0:
        top_10["Otros"] = otros

    df_top = top_10.reset_index()
    df_top.columns = ["Categoria", "Frecuencia"]
    df_top.sort_values("Frecuencia", ascending=False, inplace=True)

    total = df_top["Frecuencia"].sum()
    max_val = df_top["Frecuencia"].max()
    etiquetas_wrapped = wrap_labels(df_top["Categoria"], width=35)

    plt.figure(figsize=(9, 6))
    ax = sns.barplot(x="Frecuencia", y="Categoria", data=df_top, palette="Paired", edgecolor="black")
    ax.set_yticklabels(etiquetas_wrapped)

    offset = max_val * 0.01
    for i, valor in enumerate(df_top["Frecuencia"]):
        pct = (valor / total) * 100
        ax.text(valor + offset, i, f"{valor} ({pct:.1f}%)", va='center', fontsize=9)

    ax.set_title(f"Grupo UNSPSC (Top 10 + Otros)\nTotal códigos únicos: {df['Grupo Unspsc'].nunique()}")
    ax.set_xlabel("Frecuencia")
    ax.set_ylabel("Categoría")
    plt.xlim(0, max_val * 1.25)
    plt.tight_layout()

    guardar_grafico(plt.gcf(), "7. Grupo UNSPSC", os.path.join(ruta_guardado, "graficos"))

def graficar_top_producto_unspsc(df, ruta_guardado):
    """
    Genera gráfico de barras horizontales con el Top 10 de Producto UNSPSC + 'Otros'.
    Guarda el gráfico como 'Producto_UNSPSC.png'.
    """
    prod_counts = df["Producto Unspsc"].value_counts(dropna=False)
    top_10 = prod_counts.head(10)
    otros = prod_counts.iloc[10:].sum()

    if otros > 0:
        top_10["Otros"] = otros

    df_top = top_10.reset_index()
    df_top.columns = ["Categoria", "Frecuencia"]
    df_top.sort_values("Frecuencia", ascending=False, inplace=True)

    total = df_top["Frecuencia"].sum()
    max_val = df_top["Frecuencia"].max()
    etiquetas_wrapped = wrap_labels(df_top["Categoria"], width=35)

    plt.figure(figsize=(9, 6))
    ax = sns.barplot(x="Frecuencia", y="Categoria", data=df_top, palette="Paired", edgecolor="black")
    ax.set_yticklabels(etiquetas_wrapped)

    offset = max_val * 0.01
    for i, valor in enumerate(df_top["Frecuencia"]):
        pct = (valor / total) * 100
        ax.text(valor + offset, i, f"{valor} ({pct:.1f}%)", va='center', fontsize=9)

    ax.set_title(f"Producto UNSPSC (Top 10 + Otros)\nTotal códigos únicos: {df['Producto Unspsc'].nunique()}")
    ax.set_xlabel("Frecuencia")
    ax.set_ylabel("Categoría")
    plt.xlim(0, max_val * 1.25)
    plt.tight_layout()

    guardar_grafico(plt.gcf(), "8. Productos UNSPSC", os.path.join(ruta_guardado, "graficos"))

def graficar_verificacion_unspsc(df, ruta_guardado):
    """
    Compara el texto del Producto UNSPSC con el inicio de la Descripción Larga.
    Muestra gráfico de pastel indicando coincidencias y errores.
    Guarda el gráfico como 'Asignación_Producto_UNSPSC.png'.
    """
    # Preparación
    df["Producto UNSPSC parseado"] = df["Producto Unspsc"].apply(extraer_producto_unspc)
    df["Desc larga inicio"] = df["Descripcion Larga"].apply(extraer_primera_parte_desc_larga)

    df["Producto UNSPSC parseado normal"] = df["Producto UNSPSC parseado"].str.lower().str.strip()
    df["Desc larga inicio normal"] = df["Desc larga inicio"].str.lower().str.strip()

    df["Verificacion UNSPSC"] = (
        df["Producto UNSPSC parseado normal"] == df["Desc larga inicio normal"]
    )

    correctos = df["Verificacion UNSPSC"].sum()
    errores_df = df[~df["Verificacion UNSPSC"]]
    errores_count = errores_df["Producto Unspsc"].value_counts(dropna=False)
    top_10 = errores_count.head(10)
    otros = errores_count.iloc[10:].sum()

    etiquetas = ["Correcto"] + [str(cat) for cat in top_10.index]
    valores = [correctos] + list(top_10.values)
    if otros > 0:
        etiquetas.append("Otros")
        valores.append(otros)

    colores = plt.cm.Paired(range(len(etiquetas)))

    fig, ax = plt.subplots(figsize=(6, 5))
    dibujar_etiquetas_pie(
        fig, ax,
        etiquetas=etiquetas,
        valores=valores,
        colores=colores,
        titulo="Asignación de Producto UNSPSC en Descripción Larga"
    )

    plt.axis('equal')
    plt.tight_layout()

    guardar_grafico(fig, "9. Asignación producto en descripcion", os.path.join(ruta_guardado, "graficos"))

def graficar_cantidad_caracteristicas(df, ruta_guardado):
    """
    Genera gráfico de barras con la cantidad de productos UNSPSC según el número de características.
    Guarda el gráfico como 'Cant_caract.png'.
    """
    # Extraer características por fila
    df["Lista de caracteristicas"] = df["Descripcion Larga"].apply(extraer_caracteristicas)

    # Agrupar por producto
    agrupado = df.groupby("Producto Unspsc")["Lista de caracteristicas"].sum()
    agrupado = agrupado.apply(lambda x: set(x))

    df_carac = agrupado.reset_index()
    df_carac.columns = ["Producto Unspsc", "Set de caracteristicas"]
    df_carac["Cantidad caracteristicas"] = df_carac["Set de caracteristicas"].apply(len)

    # Clasificar por rangos
    df_carac["Grupo de caracteristicas"] = pd.cut(
        df_carac["Cantidad caracteristicas"],
        bins=[0, 1, 2, 3, 4, 5, 6, 7, np.inf],
        labels=["0", "1", "2", "3", "4", "5", "6", "7+"],
        include_lowest=True
    )

    conteo = df_carac["Grupo de caracteristicas"].value_counts().sort_index()

    plt.figure(figsize=(6, 4))
    ax = sns.barplot(x=conteo.index, y=conteo.values, palette="Set2", edgecolor="black")

    max_val = conteo.max()
    ax.set_ylim(0, max_val * 1.2)

    for i, val in enumerate(conteo.values):
        offset = val * 0.02
        ax.text(i, val + offset, str(val), ha="center", va="bottom", fontweight="bold")

    ax.set_xlabel("Cantidad de características")
    ax.set_ylabel("Cantidad de productos UNSPSC")
    ax.set_title("Productos UNSPSC según cantidad de características")
    plt.tight_layout()

    guardar_grafico(plt.gcf(), "10. Cantidad de caracteristicas", os.path.join(ruta_guardado, "graficos"))

def graficar_codigo_categoria(df, ruta_guardado):
    """
    Genera gráfico de pastel con el Top 10 de 'Codigo de Categoria' + 'Otros'.
    Guarda el gráfico como 'Codigo_categoria.png'.
    """
    cat_counts = df["Codigo de Categoria"].value_counts(dropna=False)
    top_10 = cat_counts.head(10)
    otros = cat_counts.iloc[10:].sum()

    if otros > 0:
        top_10["Otros"] = otros

    etiquetas = top_10.index.tolist()
    valores = top_10.values.tolist()
    colores = plt.cm.Paired(range(len(etiquetas)))

    fig, ax = plt.subplots(figsize=(6, 5))
    dibujar_etiquetas_pie(
        fig, ax,
        etiquetas=etiquetas,
        valores=valores,
        colores=colores,
        titulo=f"Distribución de 'Codigo de Categoria'"
    )

    plt.axis('equal')
    plt.tight_layout()

    guardar_grafico(fig, "11. Codigo categoria", os.path.join(ruta_guardado, "graficos"))

def graficar_tipo_articulo(df, ruta_guardado):
    """
    Genera gráfico de pastel con el Top 10 de 'Tipo de articulo' + 'Otros'.
    Guarda el gráfico como 'Tipo_articulo.png'.
    """
    tipo_counts = df["Tipo de articulo"].value_counts(dropna=False)
    top_10 = tipo_counts.head(10)
    otros = tipo_counts.iloc[10:].sum()

    if otros > 0:
        top_10["Otros"] = otros

    etiquetas = top_10.index.tolist()
    valores = top_10.values.tolist()
    colores = plt.cm.Paired(range(len(etiquetas)))

    fig, ax = plt.subplots(figsize=(6, 5))
    dibujar_etiquetas_pie(
        fig, ax,
        etiquetas=etiquetas,
        valores=valores,
        colores=colores,
        titulo=f"Distribución de 'Tipo de articulo'"
    )

    plt.axis('equal')
    plt.tight_layout()

    guardar_grafico(fig, "12. Tipo articulo", os.path.join(ruta_guardado, "graficos"))
