# utils/registro_historial.py

import os
import time
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError

# 📦 Configuración de conexión a la BDM (igual que en actualizar_bdm)
DB_CONFIG = {
    "usuario": "root",
    "contraseña": "Sql150796*",
    "host": "127.0.0.1",
    "puerto": 3306,
    "base_datos": "base_datos_maestra"
}


def conectar_bdm():
    """Crea y retorna un engine SQLAlchemy para la BDM."""
    url = (
        f"mysql+pymysql://{DB_CONFIG['usuario']}:{DB_CONFIG['contraseña']}@"
        f"{DB_CONFIG['host']}:{DB_CONFIG['puerto']}/{DB_CONFIG['base_datos']}"
    )
    return create_engine(url)


def registrar_diagnostico_bdm(
    catalogo_nombre: str,
    total_rows: int,
    total_dups: int,
    nuevos: int,
    actualizados: int,
    total_seg: float,
    estado: str,
    notas: str
) -> None:
    """
    Registra una entrada en la tabla diagnostic_history con la información del diagnóstico.
    """
    engine = conectar_bdm()
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    data = [{
        "timestamp": ts,
        "catalogo": catalogo_nombre,
        "filas": total_rows,
        "duplicados": total_dups,
        "nuevos": nuevos,
        "actualizados": actualizados,
        "duracion_segundos": total_seg,
        "estado": estado,
        "notas": notas
    }]
    df = pd.DataFrame(data)

    try:
        df.to_sql(
            "diagnostic_history",
            con=engine,
            if_exists="append",
            index=False
        )
        print("✅ Historial de diagnóstico registrado correctamente.")
    except SQLAlchemyError as e:
        print(f"❌ Error al registrar historial: {e}")
    except Exception as e:
        print(f"❌ Error inesperado al registrar historial: {e}")
