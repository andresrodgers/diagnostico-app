import os
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sqlalchemy import create_engine

def sugerir_codigos_para_faltantes(df_actual, top_n=1):

    # Conectar a la base de datos
    engine = create_engine("mysql+pymysql://root:Sql150796*@127.0.0.1:3306/base_datos_maestra")

    # Leer registros validados
    df_validados = pd.read_sql("SELECT description_hash, description_final, codigo FROM validated_materials", con=engine)
    df_validados = df_validados.dropna(subset=["description_final", "codigo"]).drop_duplicates()

    # Filtrar registros sin código
    df_sin_codigo = df_actual[df_actual["codigo"].isna() | (df_actual["codigo"] == "")].copy()
    if df_sin_codigo.empty:
        print("✅ No hay registros sin código UNSPSC.")
        return df_actual

    # Vectorizar descripciones
    corpus_validados = df_validados["description_final"].astype(str).tolist()
    corpus_nuevos = df_sin_codigo["description_final"].astype(str).tolist()

    vectorizer = TfidfVectorizer().fit(corpus_validados + corpus_nuevos)
    vect_validados = vectorizer.transform(corpus_validados)
    vect_nuevos = vectorizer.transform(corpus_nuevos)

    # Calcular similitud
    sim_matrix = cosine_similarity(vect_nuevos, vect_validados)

    # Sugerir códigos
    sugerencias = []
    for idx, sims in enumerate(sim_matrix):
        top_idx = sims.argmax()
        codigo_sugerido = df_validados.iloc[top_idx]["codigo"]
        df_sin_codigo.at[df_sin_codigo.index[idx], "codigo_sugerido"] = codigo_sugerido

    # Combinar con df_actual
    df_actual = df_actual.copy()
    df_actual["codigo_sugerido"] = df_actual.index.map(df_sin_codigo["codigo_sugerido"].to_dict())

    print(f"🧠 Sugerencias generadas para {len(df_sin_codigo)} registros sin código.")

    # Guardar sugerencias acumuladas
    ruta_salida = "data/processed/sugerencias_codigos_unspsc.xlsx"
    df_salida = df_sin_codigo[["description_final", "codigo_sugerido"]].copy()
    df_salida = df_salida.dropna(subset=["codigo_sugerido"])

    if not df_salida.empty:
        os.makedirs(os.path.dirname(ruta_salida), exist_ok=True)
        if os.path.exists(ruta_salida):
            df_existente = pd.read_excel(ruta_salida)
            df_salida = pd.concat([df_existente, df_salida], ignore_index=True).drop_duplicates()

        df_salida.to_excel(ruta_salida, index=False)

    return df_actual
