import os
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sqlalchemy import create_engine

def detectar_sospechosos_unspsc(df_nuevo, umbral_similitud=0.8):

    engine = create_engine("mysql+pymysql://root:Sql150796*@127.0.0.1:3306/base_datos_maestra")
    df_bdm = pd.read_sql("SELECT description_hash, description_final, codigo FROM validated_materials", con=engine)

    # Combinar catálogos para vectorizar
    df_comb = pd.concat([df_nuevo[["description_final"]], df_bdm[["description_final"]]], ignore_index=True)
    textos = df_comb["description_final"].astype(str).fillna("").tolist()

    # Vectorizar descripciones con TF-IDF
    vectorizer = TfidfVectorizer(ngram_range=(1, 2), min_df=1)
    vectores = vectorizer.fit_transform(textos)

    vectores_nuevos = vectores[:len(df_nuevo)]
    vectores_maestros = vectores[len(df_nuevo):]

    similitudes = cosine_similarity(vectores_nuevos, vectores_maestros)
    sospechosos = []

    for idx, fila in df_nuevo.iterrows():
        max_sim = similitudes[idx].max()
        if max_sim >= umbral_similitud:
            indice_similar = similitudes[idx].argmax()
            fila_bdm = df_bdm.iloc[indice_similar]
            if fila["codigo"] and fila["codigo"] != fila_bdm["codigo"]:
                sospechosos.append({
                    "description_final": fila["description_final"],
                    "codigo_asignado": fila["codigo"],
                    "codigo_sugerido": fila_bdm["codigo"],
                    "descripcion_similar": fila_bdm["description_final"],
                    "similitud": round(max_sim, 4)
                })

    df_resultado = pd.DataFrame(sospechosos)

    # Guardar archivo acumulativo
    if not df_resultado.empty:
        ruta_salida = "data/processed/sospechosos_codigos_unspsc.xlsx"
        os.makedirs(os.path.dirname(ruta_salida), exist_ok=True)

        if os.path.exists(ruta_salida):
            df_existente = pd.read_excel(ruta_salida)
            df_resultado = pd.concat([df_existente, df_resultado], ignore_index=True).drop_duplicates()

        df_resultado.to_excel(ruta_salida, index=False)

    print(f"🧐 Códigos sospechosos detectados: {len(df_resultado)}")

    # También retorna el DataFrame original con una bandera
    df_nuevo = df_nuevo.copy()
    df_nuevo["codigo_sospechoso"] = df_nuevo["description_final"].isin(df_resultado["description_final"])

    return df_nuevo