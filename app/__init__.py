from flask import Flask
from .models import db
import os
from datetime import timedelta
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# ==============================
# Crear la base de datos y tablas si no existen
# ==============================

def ensure_database_and_tables():
    DB_NAME = os.environ.get('DB_NAME', 'peluqueria_db')
    DB_USER = os.environ.get('DB_USER', 'admin')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', 'admin123')
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_PORT = os.environ.get('DB_PORT', '5432')

    # Crear base de datos si no existe
    conn = psycopg2.connect(
        dbname='postgres',
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    cur.execute(f"SELECT 1 FROM pg_database WHERE datname='{DB_NAME}';")
    exists = cur.fetchone()
    if not exists:
        print(f"Base de datos '{DB_NAME}' no existe. Creándola...")
        cur.execute(f"CREATE DATABASE {DB_NAME};")
    else:
        print(f"Base de datos '{DB_NAME}' ya existe.")
    cur.close()
    conn.close()

    # Crear tablas en la base de datos creada
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS peluquerias (
            id SERIAL PRIMARY KEY,
            nombre VARCHAR(100) NOT NULL,
            direccion TEXT,
            telefono VARCHAR(20)
        );
                
        ALTER DATABASE peluqueria_db SET TIMEZONE TO 'America/Argentina/Buenos_Aires';

        CREATE TABLE IF NOT EXISTS barberos (
            id SERIAL PRIMARY KEY,
            peluqueria_id INTEGER NOT NULL REFERENCES peluquerias(id) ON DELETE CASCADE,
            name VARCHAR(100) NOT NULL,
            porcentaje INTEGER NOT NULL,
            active BOOLEAN DEFAULT TRUE
        );

        CREATE TABLE IF NOT EXISTS metodos_pago (
            id SERIAL PRIMARY KEY,
            peluqueria_id INTEGER NOT NULL REFERENCES peluquerias(id) ON DELETE CASCADE,
            nombre VARCHAR(50) NOT NULL,
            active BOOLEAN DEFAULT TRUE
        );

        CREATE TABLE IF NOT EXISTS servicios (
            id SERIAL PRIMARY KEY,
            peluqueria_id INTEGER NOT NULL REFERENCES peluquerias(id) ON DELETE CASCADE,
            name VARCHAR(100) NOT NULL,
            active BOOLEAN DEFAULT TRUE,
            precio NUMERIC(10,2) NOT NULL,
            precio_amigo NUMERIC(10,2) DEFAULT 0,
            precio_descuento NUMERIC(10,2) DEFAULT 0
        );
                
        CREATE TABLE IF NOT EXISTS productos (
            id SERIAL PRIMARY KEY,
            peluqueria_id INTEGER NOT NULL REFERENCES peluquerias(id) ON DELETE CASCADE,
            name VARCHAR(100) NOT NULL,
            precio NUMERIC(10,2) NOT NULL,
            cantidad INTEGER,
            active BOOLEAN DEFAULT TRUE
        );

        CREATE TABLE IF NOT EXISTS turnos (
            id SERIAL PRIMARY KEY,
            date TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
            barber_id INTEGER REFERENCES barberos(id),
            service_id INTEGER REFERENCES servicios(id),
            productos_id INTEGER REFERENCES productos(id),
            cantidad INTEGER,
            peluqueria_id INTEGER NOT NULL REFERENCES peluquerias(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS pagos (
            id SERIAL PRIMARY KEY,
            appointment_id INTEGER NOT NULL REFERENCES turnos(id),
            payment_method1_id INTEGER NOT NULL REFERENCES metodos_pago(id),
            payment_method2_id INTEGER REFERENCES metodos_pago(id),
            amount_method1 NUMERIC(10,2) NOT NULL,
            amount_method2 NUMERIC(10,2),
            amount_tip NUMERIC(10,2),
            date TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
            peluqueria_id INTEGER NOT NULL REFERENCES peluquerias(id) ON DELETE CASCADE
        );
                
        CREATE TABLE IF NOT EXISTS membresias (
            id SERIAL PRIMARY KEY,
            peluqueria_id INTEGER NOT NULL REFERENCES peluquerias(id) ON DELETE CASCADE,
            cantidad INTEGER NOT NULL CHECK (cantidad > 0),
            creado_en TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            valido_hasta TIMESTAMP WITH TIME ZONE,
            canjeado BOOLEAN DEFAULT FALSE
        );

    """)
    conn.commit()

    # Verificar si la tabla 'peluquerias' está vacía
    cur.execute("SELECT COUNT(*) FROM peluquerias;")
    count = cur.fetchone()[0]

    if count == 0:
        print("Insertando peluquería inicial...")
        cur.execute("INSERT INTO peluquerias (id, nombre) VALUES (1, 'Peluquería Central');")
        conn.commit()
    else:
        print("Ya existen peluquerías registradas. No se insertó ninguna.")

    cur.close()
    conn.close()
    print("Tablas creadas o ya existentes.")

# ==============================
# Crear la app
# ==============================

def create_app():
    ensure_database_and_tables() 

    app = Flask(__name__)

    # Configuración de la base de datos PostgreSQL desde variables de entorno
    DB_NAME = os.environ.get('DB_NAME', 'peluqueria_db')
    DB_USER = os.environ.get('DB_USER', 'admin')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', 'admin123')
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_PORT = os.environ.get('DB_PORT', '5432')

    # Usar PostgreSQL
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
    )

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Clave secreta para sesiones y credenciales admin para login simple
    app.secret_key = os.environ.get('SECRET_KEY', 'clave_segura_default')
    app.config['ADMIN_USERNAME'] = DB_USER
    app.config['ADMIN_PASSWORD'] = DB_PASSWORD

    # Tiempo de expiración de la sesión
    app.permanent_session_lifetime = timedelta(minutes=15)

    # Inicializar extensión SQLAlchemy
    db.init_app(app)

    # Crear tablas automáticamente si no existen
    with app.app_context():
        from . import routes
        db.create_all()

    return app
