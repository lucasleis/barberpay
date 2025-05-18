import psycopg2
from psycopg2.extras import RealDictCursor

def get_connection():
    return psycopg2.connect(
        dbname="tu_basedatos",
        user="tu_usuario",
        password="tu_password",
        host="localhost",  # o IP/hostname si usas servidor remoto
        port=5432
    )

def obtener_peluquerias():
    conn = get_connection()
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT * FROM peluquerias")
        result = cur.fetchall()
    conn.close()
    return result

# Ejemplo de uso:
if __name__ == "__main__":
    peluquerias = obtener_peluquerias()
    for p in peluquerias:
        print(p)
