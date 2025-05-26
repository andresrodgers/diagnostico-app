# --- IMPORTACIONES NECESARIAS ---
import customtkinter as ctk  # Interfaz gráfica personalizada
from PIL import Image         # Para mostrar el logo
import re                     # Expresiones regulares
import pandas as pd           # Para manejar datos faltantes (NaN)
import os

# --- VENTANA EMERGENTE PARA PEDIR NOMBRE DE CARPETA ---
def ventana_nombre_carpeta(parent):
    # Crea una ventana secundaria (Toplevel) sobre la ventana principal
    ventana_dialogo = ctk.CTkToplevel(parent)
    ventana_dialogo.title("Nombre de Carpeta")
    ventana_dialogo.geometry("360x180")
    ventana_dialogo.configure(fg_color="#0b8e36")
    ventana_dialogo.resizable(False, False)

    # Carga y muestra el logo en la parte superior
    RUTA_ASSETS = os.path.join(os.path.dirname(__file__), '..', 'assets')
    logo_img = ctk.CTkImage(Image.open(os.path.join(RUTA_ASSETS, "logo_stockgi.png")), size=(120, 40))
    ctk.CTkLabel(ventana_dialogo, image=logo_img, text="").pack(pady=(10, 0))

    # Texto de instrucción
    ctk.CTkLabel(
        ventana_dialogo,
        text="Nombre para la carpeta de resultados:",
        text_color="#ededed",
        font=("Avenir LT Std", 13)
    ).pack(pady=(10, 5))

    # Campo de entrada para el nombre
    entrada = ctk.CTkEntry(ventana_dialogo, width=250)
    entrada.pack(pady=5)

    resultado = {"valor": None}  # Diccionario mutable para devolver el resultado

    # Acción al presionar el botón "Aceptar"
    def aceptar():
        resultado["valor"] = entrada.get()
        ventana_dialogo.destroy()

    ctk.CTkButton(
        ventana_dialogo,
        text="Aceptar",
        command=aceptar,
        font=("Avenir LT Std", 12),
        fg_color="#054118",
        hover_color="#0b8e36",
        text_color="#ededed",
        corner_radius=10
    ).pack(pady=(10, 10))

    # Modo modal: bloquea la ventana principal hasta cerrar esta
    ventana_dialogo.transient(parent)
    ventana_dialogo.grab_set()
    parent.wait_window(ventana_dialogo)

    return resultado["valor"]  # Devuelve lo ingresado


# --- EXTRAE TEXTO DESCRIPTIVO DE PRODUCTO UNSPSC ---
def extraer_producto_unspc(texto_unspc):
    if pd.isna(texto_unspc):
        return ""
    
    # Busca separar código y texto en casos como: "12345678 - Equipos médicos"
    patron = r"^[^\s]+(?:\s*-\s*|\s+)(.*)"  # Captura lo que viene después del guion o espacio
    match = re.match(patron, texto_unspc)
    if match:
        return match.group(1).strip()  # Parte textual limpia
    else:
        return texto_unspc.strip()  # Si no hay coincidencia, devuelve todo


# --- EXTRAE LA PRIMERA PARTE DE LA DESCRIPCIÓN LARGA ---
def extraer_primera_parte_desc_larga(desc_larga):
    if pd.isna(desc_larga):
        return ""
    partes = desc_larga.split(',', maxsplit=1)  # Divide solo en la primera coma
    return partes[0].strip()  # Devuelve lo que está antes de la primera coma


# --- EXTRAE CARACTERÍSTICAS CLAVE DE LA DESCRIPCIÓN LARGA ---
def extraer_caracteristicas(desc_larga):
    if pd.isna(desc_larga) or desc_larga.strip() == "":
        return []

    partes = desc_larga.split(",")  # Divide por coma
    caracteristicas = []

    for p in partes:
        p = p.strip()
        if ":" in p:
            etiqueta = p.split(":", maxsplit=1)[0].strip()  # Toma solo el nombre antes de los dos puntos
            caracteristicas.append(etiqueta)

    return caracteristicas  # Devuelve lista de etiquetas encontradas
