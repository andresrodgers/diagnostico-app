import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import textwrap
import re
from langdetect import detect, DetectorFactory
from tkinter import messagebox

from app_catalogo.helpers import (
    extraer_producto_unspc,
    extraer_primera_parte_desc_larga,
    extraer_caracteristicas
)

DetectorFactory.seed = 0  # Para detección de idioma reproducible

def normalizar_descripcion(texto):
    if pd.isna(texto) or texto == "":
        return ""
    return ",".join(sorted(texto.split(","))).strip()

def detectar_idioma(descripcion):
    if pd.isna(descripcion) or descripcion == "":
        return 'Nulo/Vacío'
    try:
        idioma = detect(descripcion)
        return 'Español' if idioma == 'es' else 'Inglés' if idioma == 'en' else 'Mezcla'
    except:
        return 'Mezcla'

def wrap_labels(labels, width=30):
    return ['\n'.join(textwrap.wrap(l, width)) for l in labels]

def guardar_grafico(fig, nombre, ruta):
    fig.savefig(os.path.join(ruta, f"{nombre}.png"), bbox_inches='tight')
    plt.close(fig)

def procesar_excel(excel_path, ruta_guardado, barra_progreso, ventana):
    total_pasos = 14
    paso_actual = 0

    def actualizar_progreso():
        nonlocal paso_actual
        progreso = paso_actual / total_pasos
        ventana.after(0, barra_progreso.set, progreso)

    try:
        os.makedirs(os.path.join(ruta_guardado, "graficos"), exist_ok=True)

        if not excel_path:
            messagebox.showerror("Error", "No seleccionaste ningún archivo.")
            return

        db = pd.read_excel(excel_path, index_col=None)
        db.rename(columns={
            "Código del Material": "Codigo Material",
            "Descripción de artículo corta": "Descripcion corta",
            "Descripción de artículo Larga": "Descripcion larga",
            "Unidad de medida principal": "Unidad de medida",
            "Grupo Norma - UNSPSC": "Grupo UNSPSC",
            "Producto - UNSPSC": "Producto UNSPSC",
            "Código de Categoria": "Codigo de Categoria",
            "Tipo de artículo": "Tipo de articulo"
        }, inplace=True)

        total_filas = len(db)

        # 1. Porcentaje de datos por columna
        porcentaje_datos = (db.notnull().sum() / total_filas) * 100

        plt.figure(figsize=(12, 5))
        ax = sns.barplot(x=porcentaje_datos.index, y=porcentaje_datos.values)
        for i, v in enumerate(porcentaje_datos.values):
            ax.text(i, v + 1, f"{v:.1f}%", ha="center", fontsize=7, fontweight="bold")

        plt.xticks(rotation=90)
        plt.ylabel("Porcentaje de datos %")
        plt.title("Porcentaje de datos presentes en cada columna")
        plt.ylim(0, 110)
        plt.tight_layout()
        plt.savefig(os.path.join(ruta_guardado, "graficos", "Porcentaje_datos.png"), bbox_inches='tight')
        plt.close()
        paso_actual += 1
        actualizar_progreso()

        # 2. Normalización de descripciones
        db["Descripcion larga normalizada"] = db["Descripcion larga"].apply(normalizar_descripcion)
        db["Descripcion corta normalizada"] = db["Descripcion corta"].apply(normalizar_descripcion)

        # 3. Duplicados y únicos
        dup_larga = db["Descripcion larga normalizada"].duplicated(keep=False)
        dup_corta = db["Descripcion corta normalizada"].duplicated(keep=False)
        val_unicos_larga = db[~dup_larga]["Descripcion larga normalizada"].nunique()
        val_unicos_corta = db[~dup_corta]["Descripcion corta normalizada"].nunique()
        dup_larga_count, dup_corta_count = dup_larga.sum(), dup_corta.sum()
        val_unicos_larga_fin = val_unicos_larga + (dup_larga_count / 2)
        val_unicos_corta_fin = val_unicos_corta + (dup_corta_count / 2)

        # Gráfico de descripciones únicas
        fig, ax = plt.subplots(figsize=(5, 5))
        etiquetas = ["Descripcion corta", "Descripcion larga"]
        valores = [val_unicos_corta_fin, val_unicos_larga_fin]
        colores = plt.cm.Paired(range(len(valores)))
        ax.bar(etiquetas, valores, color=colores, edgecolor='black')
        for i, valor in enumerate(valores):
            pct = (valor / total_filas) * 100
            ax.text(i, valor + 100, f"{int(valor)} ({pct:.2f}%)", ha='center', fontsize=10, fontweight='bold')
        ax.set_title("Descripciones únicas")
        plt.tight_layout()
        plt.savefig(os.path.join(ruta_guardado, "graficos", "Descripciones_unicas.png"), bbox_inches='tight')
        plt.close()
        paso_actual += 1
        actualizar_progreso()

        # 4. Exportar duplicados a Excel
        duplicados_larga_df = db[dup_larga].copy()
        duplicados_corta_df = db[dup_corta].copy()
        duplicados_larga_df["Código Duplicado Larga"] = duplicados_larga_df.groupby("Descripcion larga normalizada").ngroup() + 1
        duplicados_corta_df["Código Duplicado Corta"] = duplicados_corta_df.groupby("Descripcion corta normalizada").ngroup() + 1

        with pd.ExcelWriter(os.path.join(ruta_guardado, "duplicados_descripciones.xlsx")) as writer:
            duplicados_larga_df[["Código Duplicado Larga", "Descripcion larga"]].to_excel(writer, sheet_name="Duplicados Larga", index=False)
            duplicados_corta_df[["Código Duplicado Corta", "Descripcion corta"]].to_excel(writer, sheet_name="Duplicados Corta", index=False)

        # 5. Gráfico duplicados en pastel
        fig, ax = plt.subplots(figsize=(5, 5))
        valores = [dup_corta_count, dup_larga_count]
        etiquetas = [f"Corta ({dup_corta_count})", f"Larga ({dup_larga_count})"]
        colores = plt.cm.Paired(range(len(valores)))
        ax.pie(valores, startangle=90, colors=colores, wedgeprops={'edgecolor': 'black'})

        for i, size in enumerate(valores):
            pct = (size / sum(valores)) * 100
            ax.text(1.3, 1 - (i * 0.2) - 0.7, f"{etiquetas[i]}: {pct:.1f}%", fontsize=10, va='center')
            ax.scatter(1.2, 1 - (i * 0.2) - 0.7, s=100, color=colores[i], edgecolor='black')

        ax.set_title("Duplicados en Descripciones")
        plt.axis('equal')
        plt.tight_layout()
        plt.savefig(os.path.join(ruta_guardado, "graficos", "Descripciones_duplicadas.png"), bbox_inches='tight')
        plt.close()
        paso_actual += 1
        actualizar_progreso()

        # 6. Análisis de longitud en Descripción corta
        db["Total caracteres"] = db["Descripcion corta"].astype(str).str.len()
        mas_20 = (db["Total caracteres"] > 20).sum()
        menos_igual_20 = (db["Total caracteres"] <= 20).sum()
        nulos_o_vacios = db["Descripcion corta"].isnull().sum() + (db["Descripcion corta"] == "").sum()

        etiquetas_len = ["Más de 20", "20 o menos", "Nulos/vacíos"]
        valores_len = [mas_20, menos_igual_20, nulos_o_vacios]

        fig, ax = plt.subplots(figsize=(5, 5))
        colors_len = plt.cm.Paired(range(len(valores_len)))

        ax.pie(
            valores_len,
            startangle=90,
            colors=colors_len,
            wedgeprops={'edgecolor': 'black'}
        )

        total_len = sum(valores_len)
        y_offset = 0.7
        for i, size in enumerate(valores_len):
            percentage = (size / total_len) * 100
            label_txt = f"{etiquetas_len[i]}: {size} ({percentage:.1f}%)"
            ax.text(1.3, 1 - (i * 0.2) - y_offset, label_txt, fontsize=10, va='center')
            ax.scatter(1.2, 1 - (i * 0.2) - y_offset, s=100, color=colors_len[i], edgecolor='black', zorder=10)

        fig.suptitle('Falta de información: Descripción Corta', fontsize=12,
                     ha='center', va='top', y=0.92, x=0.7)
        plt.axis('equal')
        plt.tight_layout()
        plt.savefig(os.path.join(ruta_guardado, "graficos", "Falta_informacion.png"), bbox_inches='tight')
        plt.close()
        paso_actual += 1
        actualizar_progreso()

        # 7. Detección de idioma en Descripción larga
        db["Idioma"] = db["Descripcion larga"].apply(detectar_idioma)
        idiomas_count = db["Idioma"].value_counts()

        etiquetas_idioma = idiomas_count.index.tolist()
        valores_idioma = idiomas_count.values.tolist()

        fig, ax = plt.subplots(figsize=(5, 5))
        colors_idioma = plt.cm.Paired(range(len(valores_idioma)))

        ax.pie(
            valores_idioma,
            startangle=90,
            colors=colors_idioma,
            wedgeprops={'edgecolor': 'black'}
        )

        total_idioma = sum(valores_idioma)
        y_offset = 0.7
        for i, size in enumerate(valores_idioma):
            porcentaje = (size / total_idioma) * 100
            label_txt = f"{etiquetas_idioma[i]}: {size} ({porcentaje:.1f}%)"
            ax.text(1.3, 1 - (i * 0.2) - y_offset, label_txt, fontsize=10, va='center')
            ax.scatter(1.2, 1 - (i * 0.2) - y_offset, s=100, color=colors_idioma[i], edgecolor='black', zorder=10)

        fig.suptitle("Distribución de Idiomas: Descripción larga", fontsize=12,
                     ha='center', va='top', y=0.92, x=0.7)
        plt.axis('equal')
        plt.tight_layout()
        plt.savefig(os.path.join(ruta_guardado, "graficos", "Desc_idioma.png"), bbox_inches='tight')
        plt.close()
        paso_actual += 1
        actualizar_progreso()

        # 8. Distribución de valores en Unidad de medida
        valores_unicos_um = db['Unidad de medida'].value_counts(dropna=False)
        nulos_um = valores_unicos_um.get(np.nan, 0)
        valores_unicos_um = valores_unicos_um.dropna()

        etiquetas_um = list(valores_unicos_um.index) + ["Nulos"]
        totales_um = list(valores_unicos_um.values) + [nulos_um]

        fig, ax = plt.subplots(figsize=(5, 5))
        colors_um = plt.cm.Paired(range(len(totales_um)))

        ax.pie(
            totales_um,
            startangle=90,
            colors=colors_um,
            wedgeprops={'edgecolor': 'black'}
        )

        total_um = sum(totales_um)
        y_offset = 0.7

        for i, size in enumerate(totales_um):
            porcentaje = (size / total_um) * 100
            label_txt = f"{etiquetas_um[i]}: {size} ({porcentaje:.1f}%)"
            ax.text(1.3, 1.25 - (i * 0.11) - y_offset, label_txt, fontsize=10, va='center')
            ax.scatter(1.2, 1.25 - (i * 0.11) - y_offset, s=100, color=colors_um[i],
                       edgecolor='black', zorder=10)

        fig.suptitle(f"Distribución de valores en Unidad de medida\n(Total: {total_um})",
                     fontsize=12, ha='center', va='top', y=0.92, x=0.7)
        plt.axis('equal')
        plt.tight_layout()
        plt.savefig(os.path.join(ruta_guardado, "graficos", "Unidades_medida.png"), bbox_inches='tight')
        plt.close()
        paso_actual += 1
        actualizar_progreso()

        # 9. Top 10 de Grupo UNSPSC (barras horizontales)
        def wrap_labels(labels, width=30):
            return ['\n'.join(textwrap.wrap(l, width)) for l in labels]

        grupo_unique_count = db["Grupo UNSPSC"].nunique()
        grupo_counts = db["Grupo UNSPSC"].value_counts(dropna=False)
        top_10_gn = grupo_counts.head(10)
        otros_gn = grupo_counts.iloc[10:].sum()
        top_10_gn["Otros"] = otros_gn

        gn_df = top_10_gn.reset_index()
        gn_df.columns = ["Categoria", "Frecuencia"]
        gn_df.sort_values("Frecuencia", ascending=False, inplace=True)

        total_gn = gn_df["Frecuencia"].sum()
        max_val = gn_df["Frecuencia"].max()

        plt.figure(figsize=(9, 6))
        barras_gn = sns.barplot(
            x="Frecuencia",
            y="Categoria",
            data=gn_df,
            palette="Paired",
            edgecolor="black"
        )

        categorias_wrapped = wrap_labels(gn_df["Categoria"], width=35)
        barras_gn.set_yticklabels(categorias_wrapped)
        plt.xlim(0, max_val * 1.25)
        barras_gn.set_title(f"Grupo UNSPSC (Top 10 + Otros)\nTotal códigos únicos: {grupo_unique_count}")
        barras_gn.set_xlabel("Frecuencia")
        barras_gn.set_ylabel("Categoría")

        offset = max_val * 0.01
        for i, valor in enumerate(gn_df["Frecuencia"]):
            pct = (valor / total_gn) * 100
            barras_gn.text(valor + offset, i, f"{valor} ({pct:.1f}%)", va='center', fontsize=9)

        plt.tight_layout()
        plt.savefig(os.path.join(ruta_guardado, "graficos", "Grupo_UNSPSC.png"), bbox_inches='tight')
        plt.close()
        paso_actual += 1
        actualizar_progreso()

        # 10. Top 10 Producto UNSPSC (barras horizontales)
        total_unique = db["Producto UNSPSC"].nunique()
        prod_counts = db["Producto UNSPSC"].value_counts(dropna=False)
        top_10_prod = prod_counts.head(10)
        otros_prod = prod_counts.iloc[10:].sum()
        top_10_prod["Otros"] = otros_prod

        prod_df = top_10_prod.reset_index()
        prod_df.columns = ["Categoria", "Frecuencia"]
        prod_df.sort_values("Frecuencia", ascending=False, inplace=True)

        total_prod = prod_df["Frecuencia"].sum()
        max_val = prod_df["Frecuencia"].max()

        plt.figure(figsize=(9, 6))
        barras_prod = sns.barplot(
            x="Frecuencia",
            y="Categoria",
            data=prod_df,
            palette="Paired",
            edgecolor="black"
        )

        categorias_wrapped = wrap_labels(prod_df["Categoria"], width=35)
        barras_prod.set_yticklabels(categorias_wrapped)
        plt.xlim(0, max_val * 1.25)
        barras_prod.set_title(f"Producto UNSPSC (Top 10 + Otros)\nTotal códigos únicos: {total_unique}")
        barras_prod.set_xlabel("Frecuencia")
        barras_prod.set_ylabel("Categoría")

        offset = max_val * 0.01
        for i, valor in enumerate(prod_df["Frecuencia"]):
            pct = (valor / total_prod) * 100
            barras_prod.text(valor + offset, i, f"{valor} ({pct:.1f}%)", va='center', fontsize=9)

        plt.tight_layout()
        plt.savefig(os.path.join(ruta_guardado, "graficos", "Producto_UNSPSC.png"), bbox_inches='tight')
        plt.close()
        paso_actual += 1
        actualizar_progreso()

        # 11. Comparación Producto UNSPSC vs Descripción Larga

        db["Producto UNSPSC parseado"] = db["Producto UNSPSC"].apply(extraer_producto_unspc)
        db["Desc larga inicio"] = db["Descripcion larga"].apply(extraer_primera_parte_desc_larga)

        db["Producto UNSPSC parseado normal"] = db["Producto UNSPSC parseado"].str.lower().str.strip()
        db["Desc larga inicio normal"] = db["Desc larga inicio"].str.lower().str.strip()

        db["Verificacion UNSPSC"] = (
            db["Producto UNSPSC parseado normal"] == db["Desc larga inicio normal"]
        )

        correct_count = db["Verificacion UNSPSC"].sum()
        no_correct_df = db[~db["Verificacion UNSPSC"]]
        unspsc_counts = no_correct_df["Producto UNSPSC"].value_counts(dropna=False)

        top_10 = unspsc_counts.head(10)
        others_count = unspsc_counts.iloc[10:].sum()

        labels = ["Correcto"]
        values = [correct_count]

        for cat, val in top_10.items():
            labels.append(str(cat))
            values.append(val)

        if others_count > 0:
            labels.append("Otros")
            values.append(others_count)

        colors_coinc = plt.cm.Paired(range(len(labels)))
        fig, ax = plt.subplots(figsize=(6, 6))
        ax.pie(
            values,
            startangle=90,
            colors=colors_coinc,
            wedgeprops={'edgecolor': 'black'}
        )

        total = sum(values)
        y_offset = 0.7
        for i, size in enumerate(values):
            percentage = (size / total) * 100
            label_txt = f"{labels[i]}: {size} ({percentage:.1f}%)"
            ax.text(1.3, 1.25 - (i * 0.11) - y_offset, label_txt, fontsize=10, va='center')
            ax.scatter(1.2, 1.25 - (i * 0.11) - y_offset, s=100, color=colors_coinc[i], edgecolor='black', zorder=10)

        fig.suptitle("Asignación de Producto UNSPSC en Descripción Larga",
                     fontsize=12, ha='center', va='top', y=0.92, x=0.85)
        plt.axis('equal')
        plt.savefig(os.path.join(ruta_guardado, "graficos", "Asignación_Producto_UNSPSC.png"), bbox_inches='tight')
        plt.close()
        paso_actual += 1
        actualizar_progreso()

        # 12. Análisis de características por producto UNSPSC

        db["Lista de caracteristicas"] = db["Descripcion larga"].apply(extraer_caracteristicas)

        agrupado = db.groupby("Producto UNSPSC")["Lista de caracteristicas"].sum()
        agrupado = agrupado.apply(lambda x: set(x))

        df_carac = agrupado.reset_index()
        df_carac.columns = ["Producto UNSPSC", "Set de caracteristicas"]
        df_carac["Cantidad caracteristicas"] = df_carac["Set de caracteristicas"].apply(len)

        df_carac["Grupo de caracteristicas"] = pd.cut(
            df_carac["Cantidad caracteristicas"],
            bins=[0, 1, 2, 3, 4, 5, 6, 7, np.inf],
            labels=["0", "1", "2", "3", "4", "5", "6", "7+"],
            include_lowest=True
        )

        conteo_carac = df_carac["Grupo de caracteristicas"].value_counts().sort_index()

        db["Cantidad de caracteristicas (por fila)"] = db["Lista de caracteristicas"].apply(len)

        plt.figure(figsize=(6, 4))
        ax = sns.barplot(
            x=conteo_carac.index,
            y=conteo_carac.values,
            palette="Set2",
            edgecolor="black"
        )

        max_val = conteo_carac.max()
        ax.set_ylim(0, max_val * 1.2)

        for i, val in enumerate(conteo_carac.values):
            offset = val * 0.02
            ax.text(i, val + offset, str(val), ha="center", va="bottom", fontweight="bold")

        ax.set_xlabel("Cantidad de características")
        ax.set_ylabel("Cantidad de productos UNSPSC")
        ax.set_title("Productos UNSPSC según cantidad de características")

        plt.tight_layout()
        plt.savefig(os.path.join(ruta_guardado, "graficos", "Cant_caract.png"), bbox_inches='tight')
        plt.close()
        paso_actual += 1
        actualizar_progreso()

        # 13. Gráfico de Código de Categoría

        cat_counts = db["Codigo de Categoria"].value_counts(dropna=False)
        total_cat = cat_counts.sum()

        top_10_cat = cat_counts.head(10)
        otros_cat = cat_counts.iloc[10:].sum()
        if otros_cat > 0:
            top_10_cat["Otros"] = otros_cat

        etiquetas_cat = top_10_cat.index.tolist()
        valores_cat = top_10_cat.values.tolist()

        colors_cat = plt.cm.Paired(range(len(etiquetas_cat)))
        fig, ax = plt.subplots(figsize=(5, 5))

        ax.pie(
            valores_cat,
            startangle=90,
            colors=colors_cat,
            wedgeprops={"edgecolor": "black"}
        )

        suma_cat = sum(valores_cat)
        y_offset = 0.7
        for i, size in enumerate(valores_cat):
            porcentaje = (size / suma_cat) * 100
            label_txt = f"{etiquetas_cat[i]} ({size}): {porcentaje:.1f}%"
            ax.text(1.3, 1.25 - (i * 0.2) - y_offset, label_txt, fontsize=10, va="center")
            ax.scatter(1.2, 1.25 - (i * 0.2) - y_offset, s=100,
                       color=colors_cat[i], edgecolor="black", zorder=10)

        fig.suptitle(f"Distribución de 'Codigo de Categoria' (Total: {total_cat})",
                     fontsize=12, ha='center', va='top', y=0.92, x=0.7)

        plt.savefig(os.path.join(ruta_guardado, "graficos", "Codigo_categoria.png"), bbox_inches='tight')
        plt.close()
        paso_actual += 1
        actualizar_progreso()

        # 14. Gráfico de Tipo de artículo

        tipo_counts = db["Tipo de articulo"].value_counts(dropna=False)
        total_tipo = tipo_counts.sum()

        top_10_tipo = tipo_counts.head(10)
        otros_tipo = tipo_counts.iloc[10:].sum()
        if otros_tipo > 0:
            top_10_tipo["Otros"] = otros_tipo

        etiquetas_tipo = top_10_tipo.index.tolist()
        valores_tipo = top_10_tipo.values.tolist()

        colors_tipo = plt.cm.Paired(range(len(etiquetas_tipo)))
        fig, ax = plt.subplots(figsize=(5, 5))

        ax.pie(
            valores_tipo,
            startangle=90,
            colors=colors_tipo,
            wedgeprops={"edgecolor": "black"}
        )

        suma_tipo = sum(valores_tipo)
        y_offset = 0.7
        for i, size in enumerate(valores_tipo):
            porcentaje = (size / suma_tipo) * 100
            label_txt = f"{etiquetas_tipo[i]} ({size}): {porcentaje:.1f}%"
            ax.text(1.3, 1.2 - (i * 0.2) - y_offset, label_txt, fontsize=10, va="center")
            ax.scatter(1.2, 1.2 - (i * 0.2) - y_offset, s=100,
                       color=colors_tipo[i], edgecolor="black", zorder=10)

        fig.suptitle(f"Distribución de 'Tipo de articulo' (Total: {total_tipo})",
                     fontsize=12, ha='center', va='top', y=0.92, x=0.7)

        plt.axis("equal")
        plt.savefig(os.path.join(ruta_guardado, "graficos", "Tipo_articulo.png"), bbox_inches='tight')
        plt.close()
        paso_actual += 1
        actualizar_progreso()

        # 15. Exportación del DataFrame completo

        db.to_excel(os.path.join(ruta_guardado, "Diagnostico.xlsx"), index=False)
        ventana.after(0, barra_progreso.set, 1)
        ventana.after(0, lambda: messagebox.showinfo("Éxito", "Análisis completado."))
        ventana.after(0, barra_progreso.set, 0)

    except Exception as e:
        ventana.after(0, barra_progreso.set, 0)
        mensaje_error = str(e)
        ventana.after(0, lambda: messagebox.showerror("Error", f"Ocurrió un error:\n{mensaje_error}"))
