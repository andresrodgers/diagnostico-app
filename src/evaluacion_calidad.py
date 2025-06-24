
import pandas as pd

def evaluar_calidad_por_registro(df):
    df = df.copy()

    puntajes = []

    for idx, row in df.iterrows():
        puntaje = 0

        # 1. Tiene código UNSPSC
        if pd.notna(row.get("codigo")) and str(row["codigo"]).strip() != "":
            puntaje += 25

        # 2. Descripciones completas
        if pd.notna(row.get("Descripcion Larga")) and str(row["Descripcion Larga"]).strip() != "":
            puntaje += 10
        if pd.notna(row.get("Descripcion Corta")) and str(row["Descripcion Corta"]).strip() != "":
            puntaje += 10

        # 3. Idioma identificado
        idioma = row.get("Idioma", "")
        if idioma and idioma.lower() in ["es", "en", "español", "ingles"]:
            puntaje += 15

        # 4. No es duplicado
        if not row.get("duplicado_larga", False):
            puntaje += 10
        if not row.get("duplicado_corta", False):
            puntaje += 10

        # 5. Características suficientes
        if pd.notna(row.get("Caracteristicas")):
            num_carac = len([c for c in str(row["Caracteristicas"]).split(",") if c.strip()])
            if num_carac >= 3:
                puntaje += 20

        puntajes.append(puntaje)

    df["puntaje_calidad"] = puntajes
    df["calidad"] = df["puntaje_calidad"].apply(
        lambda x: "Alta" if x >= 80 else "Media" if x >= 50 else "Baja"
    )

    return df
