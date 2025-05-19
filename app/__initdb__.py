import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

DB_NAME = "peluqueria_db"
DB_USER = "admin"
DB_PASSWORD = "admin123"
DB_HOST = "localhost"
DB_PORT = "5432"

# Sentencias SQL para crear tablas
CREATE_TABLES_SQL = """
    CREATE TABLE IF NOT EXISTS peluquerias (
        id SERIAL PRIMARY KEY,
        nombre VARCHAR(100) NOT NULL,
        direccion TEXT,
        telefono VARCHAR(20)
    );

    CREATE TABLE IF NOT EXISTS barberos (
        id SERIAL PRIMARY KEY,
        peluqueria_id INTEGER NOT NULL REFERENCES peluquerias(id) ON DELETE CASCADE,
        name VARCHAR(100) NOT NULL,
        active BOOLEAN DEFAULT TRUE
    );

    CREATE TABLE IF NOT EXISTS metodos_pago (
        id SERIAL PRIMARY KEY,
        peluqueria_id INTEGER NOT NULL REFERENCES peluquerias(id) ON DELETE CASCADE,
        nombre VARCHAR(50) UNIQUE NOT NULL,
        active BOOLEAN DEFAULT TRUE
    );

    CREATE TABLE IF NOT EXISTS servicios (
        id SERIAL PRIMARY KEY,
        peluqueria_id INTEGER NOT NULL REFERENCES peluquerias(id) ON DELETE CASCADE,
        name VARCHAR(100) NOT NULL,
        precio NUMERIC(10,2) NOT NULL
    );

    CREATE TABLE IF NOT EXISTS turnos (
        id SERIAL PRIMARY KEY,
        date TIMESTAMP NOT NULL DEFAULT NOW(),
        barber_id INTEGER REFERENCES barberos(id),
        service_id INTEGER REFERENCES servicios(id),
        peluqueria_id INTEGER NOT NULL REFERENCES peluquerias(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS pagos (
        id SERIAL PRIMARY KEY,
        appointment_id INTEGER REFERENCES turnos(id),
        amount NUMERIC(10,2) NOT NULL,
        payment_method_id INTEGER REFERENCES metodos_pago(id),
        date TIMESTAMP NOT NULL DEFAULT NOW(),
        peluqueria_id INTEGER NOT NULL REFERENCES peluquerias(id) ON DELETE CASCADE
    );
"""


def create_database():
    # Conectarse a la base de datos 'postgres' para crear la DB si no existe
    conn = psycopg2.connect(
        dbname="postgres",
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()

    # Verificar si la base de datos existe
    cur.execute(f"SELECT 1 FROM pg_database WHERE datname='{DB_NAME}';")
    exists = cur.fetchone()
    if not exists:
        print(f"Base de datos '{DB_NAME}' no existe. Creándola...")
        cur.execute(f"CREATE DATABASE {DB_NAME};")
    else:
        print(f"Base de datos '{DB_NAME}' ya existe.")

    cur.close()
    conn.close()

def create_tables():
    # Conectarse a la base de datos creada y crear las tablas
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
    cur = conn.cursor()
    cur.execute(CREATE_TABLES_SQL)
    conn.commit()
    cur.close()
    conn.close()
    print("Tablas creadas o ya existentes.")

if __name__ == "__main__":
    create_database()
    create_tables()
