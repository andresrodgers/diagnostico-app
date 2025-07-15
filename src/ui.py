# ui.py

import os
from datetime import datetime
import threading
import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image

from diagnostico import procesar_excel

# Ruta a carpeta de assets (logo, ícono)
RUTA_ASSETS = os.path.join(os.path.dirname(__file__), 'assets')

# --- CONFIGURACIÓN DE VENTANA PRINCIPAL ---
ventana = ctk.CTk()
ventana.title("Diagnóstico de Catálogo")
ventana.geometry("500x250")
ventana.resizable(False, False)

# Intento de carga de ícono
ico_path = os.path.join(RUTA_ASSETS, "ico_stockgi.ico")
if os.path.exists(ico_path):
    try:
        ventana.iconbitmap(ico_path)
    except Exception as e:
        print(f"⚠️ No se pudo cargar el ícono: {e}")
else:
    print(f"⚠️ Ícono no encontrado en: {ico_path}")

ventana.configure(fg_color="#0b8e36")
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("green")

# Barra de progreso global (declarada en iniciar_app)
barra_progreso = None

# --- FUNCIÓN PARA SELECCIÓN Y LANZAMIENTO DE PROCESO ---
def seleccionar_archivos():
    excel_path = filedialog.askopenfilename(
        title="Selecciona archivo Excel",
        filetypes=[("Excel files", "*.xlsx *.xls")]
    )
    if not excel_path:
        messagebox.showwarning("Advertencia", "No seleccionaste archivo Excel.")
        return

    base_folder = filedialog.askdirectory(
        title="Selecciona carpeta base de resultados"
    )
    if not base_folder:
        messagebox.showwarning("Advertencia", "No seleccionaste carpeta base.")
        return

    nombre_archivo = os.path.splitext(os.path.basename(excel_path))[0]
    timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M")
    nombre_carpeta = f"{timestamp} Diagnostico {nombre_archivo}"

    ruta_guardado = os.path.join(base_folder, nombre_carpeta)
    os.makedirs(os.path.join(ruta_guardado, "graficos"), exist_ok=True)

    hilo = threading.Thread(
        target=procesar_excel,
        args=(excel_path, ruta_guardado, barra_progreso, ventana),
        daemon=True
    )
    hilo.start()

# --- INICIAR INTERFAZ GRÁFICA ---
def iniciar_app():
    global barra_progreso

    # Carga del logo
    logo_path = os.path.join(RUTA_ASSETS, "logo_stockgi.png")
    try:
        logo_img = ctk.CTkImage(Image.open(logo_path), size=(140, 50))
    except Exception:
        print(f"⚠️ Logo no encontrado en: {logo_path}")
        logo_img = None

    # Logo superior
    logo_frame = ctk.CTkFrame(ventana, fg_color="#0b8e36", corner_radius=10)
    logo_frame.pack(pady=(15, 5))
    if logo_img:
        ctk.CTkLabel(logo_frame, image=logo_img, text="").pack(padx=5, pady=5)
    else:
        ctk.CTkLabel(
            logo_frame,
            text="Diagnóstico App",
            font=("Roboto", 20, "bold"),
            text_color="#ededed"
        ).pack(padx=5, pady=5)

    # Título
    titulo_frame = ctk.CTkFrame(ventana, fg_color="#0b8e36", corner_radius=10)
    titulo_frame.pack(pady=(5, 10))
    ctk.CTkLabel(
        titulo_frame,
        text="Diagnóstico de Catálogo",
        font=("Avenir LT Std", 16, "bold"),
        text_color="#ededed"
    ).pack(padx=10, pady=5)

    # Botón principal
    boton_frame = ctk.CTkFrame(ventana, fg_color="#0b8e36", corner_radius=15)
    boton_frame.pack(pady=(5, 10))
    ctk.CTkButton(
        boton_frame,
        text="Seleccionar archivo y carpeta",
        command=seleccionar_archivos,
        font=("Avenir LT Std", 13, "bold"),
        fg_color="#054118",
        text_color="#ededed",
        hover_color="#0b8e36",
        border_color="#054118",
        border_width=2,
        corner_radius=15,
        width=250,
        height=40
    ).pack(padx=2, pady=2)

    # Barra de progreso
    barra_frame = ctk.CTkFrame(ventana, fg_color="#0b8e36", corner_radius=15)
    barra_frame.pack(pady=(5, 10))

    barra_progreso = ctk.CTkProgressBar(
        barra_frame,
        width=400,
        height=20,
        fg_color="#ededed",
        progress_color="#054118",
        corner_radius=15
    )
    barra_progreso.set(0)
    barra_progreso.pack(padx=2, pady=5)

    # Lanzar loop principal
    ventana.mainloop()
