
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import DBSCAN
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def agrupar_registros_similares(df, columna_descripcion='description_final', eps=0.3, min_samples=2):
    # Preprocesar textos
    textos = df[columna_descripcion].astype(str).fillna("").tolist()
    
    # Vectorizar con TF-IDF
    vectorizer = TfidfVectorizer(ngram_range=(1, 2), min_df=1)
    vectores = vectorizer.fit_transform(textos)
    
    # Calcular similitud
    sim_matrix = cosine_similarity(vectores)
    
    # Clustering con DBSCAN sobre la matriz de similitud
    clustering = DBSCAN(eps=eps, min_samples=min_samples, metric='precomputed')
    labels = clustering.fit_predict(1 - sim_matrix)  # 1 - sim = distancia
    
    df["grupo_similar"] = labels
    df_grupos = df[df["grupo_similar"] != -1].copy()
    
    return df_grupos
