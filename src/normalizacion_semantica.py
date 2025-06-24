
# normalizacion_semantica.py

import pandas as pd
from sqlalchemy import create_engine

# Configuración de conexión a la base de datos
DB_CONFIG = {
    "usuario": "root",
    "contraseña": "Sql150796*",
    "host": "127.0.0.1",
    "puerto": 3306,
    "base_datos": "base_datos_maestra"
}

def conectar_bdm():
    engine = create_engine(f"mysql+pymysql://{DB_CONFIG['usuario']}:{DB_CONFIG['contraseña']}@{DB_CONFIG['host']}:{DB_CONFIG['puerto']}/{DB_CONFIG['base_datos']}")
    return engine

def cargar_diccionario_jerarquico(engine):
    query = "SELECT code_v26, name, hierarchy_level FROM unspsc_expected_characteristics"
    return pd.read_sql(query, engine)

def asignar_jerarquia_codigo_nuevo(df_nuevo, diccionario):
    jerarquias = []
    codigos_existentes = diccionario["code_v26"].unique()

    for codigo in df_nuevo["codigo"].unique():
        if codigo not in codigos_existentes:
            claves = df_nuevo[df_nuevo["codigo"] == codigo]["name"].unique()
            coincidencias = diccionario[diccionario["name"].isin(claves)]
            jerarquia_sugerida = coincidencias.groupby("name")["hierarchy_level"].agg(lambda x: x.mode().iloc[0] if not x.mode().empty else None).to_dict()
            for clave in claves:
                jerarquias.append({
                    "codigo": codigo,
                    "name": clave,
                    "jerarquia_sugerida": jerarquia_sugerida.get(clave, None)
                })
    return pd.DataFrame(jerarquias)

def detectar_y_corregir_errores(df_nuevo, diccionario):
    validas = diccionario[["code_v26", "name"]].drop_duplicates()
    df_nuevo["valido"] = df_nuevo.apply(lambda x: (x["codigo"], x["name"]) in set(tuple(row) for row in validas.values), axis=1)
    no_validos = df_nuevo[df_nuevo["valido"] == False]

    posibles_reasignaciones = []
    for _, row in no_validos.iterrows():
        match_valor = diccionario[diccionario["name"].str.contains(row["value"], case=False, na=False)]
        if not match_valor.empty:
            for _, mv in match_valor.iterrows():
                posibles_reasignaciones.append({
                    "codigo": row["codigo"],
                    "clave_detectada": row["name"],
                    "valor": row["value"],
                    "clave_sugerida": mv["name"],
                    "jerarquia_sugerida": mv["hierarchy_level"]
                })
    return pd.DataFrame(posibles_reasignaciones)
