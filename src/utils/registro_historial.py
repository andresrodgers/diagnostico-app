import mysql.connector
from datetime import datetime, timedelta

def registrar_diagnostico_bdm(
    catalogo_nombre, total_rows, total_dups, nuevos, actualizados,
    total_seg, estado, notas=""
):
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="diagnostico_app",
            password="tu_clave",  # reemplaza por tu contraseña real
            database="base_datos_maestra"
        )
        cursor = conn.cursor()

        tiempo = str(timedelta(seconds=round(total_seg)))

        insert_query = """
        INSERT INTO diagnostic_history (
            catalog_name, analysis_date, total_rows, total_duplicates,
            new_materials, updated_materials, total_time, status, notes
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        valores = (
            catalogo_nombre,
            datetime.now(),
            total_rows,
            total_dups,
            nuevos,
            actualizados,
            tiempo,
            estado,
            notas
        )

        cursor.execute(insert_query, valores)
        conn.commit()
        cursor.close()
        conn.close()
        print("✅ Diagnóstico registrado en BDM")

    except Exception as e:
        print(f"❌ Error al registrar diagnóstico: {e}")
