import psycopg2
from psycopg2.extras import RealDictCursor
import os

def get_connection():
    return psycopg2.connect(
        dbname=os.getenv('DB_NAME', 'peluqueria_db'),
        user=os.getenv('DB_USER', 'admin'),
        password=os.getenv('DB_PASSWORD', 'admin123'),
        host=os.getenv('DB_HOST', 'db'),
        port=int(os.getenv('DB_PORT', 5432))
    )

def obtener_peluquerias():
    conn = get_connection()
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT * FROM peluquerias")
        result = cur.fetchall()
    conn.close()
    return result

def buscar_peluqueria_por_nombre(nombre):
    conn = get_connection()
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT * FROM peluquerias WHERE nombre = %s", (nombre,))
        result = cur.fetchall()
    conn.close()
    return result

# Ejemplo de uso:
if __name__ == "__main__":
    peluquerias = obtener_peluquerias()
    for p in peluquerias:
        print(p)

    nombre = "Peluquería Central"
    resultado = buscar_peluqueria_por_nombre(nombre)
    for p in resultado:
        print(p)
