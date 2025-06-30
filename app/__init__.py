from flask import Flask
from flask_wtf import CSRFProtect 
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
    cur.execute("SELECT 1 FROM pg_database WHERE datname = %s;", (DB_NAME,))
    exists = cur.fetchone()
    if not exists:
        print(f"Base de datos '{DB_NAME}' no existe. Creándola...")
        cur.execute(f"CREATE DATABASE {DB_NAME};")
    else:
        print(f"Base de datos '{DB_NAME}' ya existe.")
    cur.close()
    conn.close()

    # Crear tablas
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
            comision_empleado NUMERIC(5,2) DEFAULT 1.0 CHECK (comision_empleado >= 1 AND comision_empleado <= 100),
            active BOOLEAN DEFAULT TRUE
        );
                
        CREATE TABLE IF NOT EXISTS tipos_membresia (
            id SERIAL PRIMARY KEY,
            nombre VARCHAR(100) NOT NULL,
            precio NUMERIC(10,2) NOT NULL,
            usos INTEGER NOT NULL,
            active BOOLEAN DEFAULT TRUE,
            servicio_id INTEGER NOT NULL REFERENCES servicios(id),
            peluqueria_id INTEGER NOT NULL REFERENCES peluquerias(id) ON DELETE CASCADE
        );
                             
        CREATE TABLE IF NOT EXISTS membresias (
            id SERIAL PRIMARY KEY,
            tipo_membresia_id INTEGER NOT NULL REFERENCES tipos_membresia(id),
            usos_disponibles INTEGER NOT NULL,
            fecha_compra TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            peluqueria_id INTEGER NOT NULL REFERENCES peluquerias(id) ON DELETE CASCADE,
            active BOOLEAN DEFAULT TRUE,
            id_usuario INTEGER UNIQUE  
        );

        CREATE TABLE IF NOT EXISTS turnos (
            id SERIAL PRIMARY KEY,
            date TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
            barber_id INTEGER REFERENCES barberos(id),
            service_id INTEGER REFERENCES servicios(id),
            membresia_id INTEGER REFERENCES membresias(id),
            peluqueria_id INTEGER NOT NULL REFERENCES peluquerias(id) ON DELETE CASCADE,

            tipo_precio_servicio TEXT CHECK (tipo_precio_servicio IN ('comun', 'amigo', 'descuento')),
            precio_aplicado NUMERIC(10,2) 
        );

        CREATE TABLE IF NOT EXISTS productos_turno (
            id SERIAL PRIMARY KEY,
            turno_id INTEGER NOT NULL REFERENCES turnos(id) ON DELETE CASCADE,
            producto_id INTEGER NOT NULL REFERENCES productos(id),
            cantidad INTEGER NOT NULL,
            precio_unitario NUMERIC(10,2) NOT NULL
        );

        CREATE TABLE IF NOT EXISTS pagos (
            id SERIAL PRIMARY KEY,
            appointment_id INTEGER NOT NULL REFERENCES turnos(id),
            membresia_comprada_id INTEGER REFERENCES membresias(id),
            payment_method1_id INTEGER NOT NULL REFERENCES metodos_pago(id),
            payment_method2_id INTEGER REFERENCES metodos_pago(id),
            amount_method1 NUMERIC(10,2) NOT NULL,
            amount_method2 NUMERIC(10,2),
            amount_tip NUMERIC(10,2),
            date TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
            peluqueria_id INTEGER NOT NULL REFERENCES peluquerias(id) ON DELETE CASCADE
        );

    """)
    conn.commit()

    try:
        cur.execute("ALTER TABLE usuario ADD COLUMN rol VARCHAR(20) DEFAULT 'barber';")
        print("Columna 'rol' agregada a tabla 'usuario'.")
    except psycopg2.errors.DuplicateColumn:
        conn.rollback()
        print("La columna 'rol' ya existe en la tabla 'usuario'.")

    # Verificar si la tabla 'peluquerias' está vacía
    cur.execute("SELECT COUNT(*) FROM peluquerias;")
    count = cur.fetchone()[0]

    if count == 0:
        print("Insertando peluquería inicial...")
        cur.execute(
            "INSERT INTO peluquerias (id, nombre) VALUES (%s, %s);",
            (1, 'Peluquería Central')
        )
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

    # Seguridad de cookies
    app.config.update(
        SESSION_COOKIE_SECURE=True,      # Solo se envían por HTTPS
        SESSION_COOKIE_HTTPONLY=True,    # No accesible desde JavaScript
        SESSION_COOKIE_SAMESITE='Lax',   # Protección CSRF
        WTF_CSRF_TIME_LIMIT=None         # (opcional) desactiva expiración del token CSRF
    )

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

    # Clave secreta para sesiones y CSRF
    app.secret_key = os.environ.get('SECRET_KEY', 'clave_segura_default')
    app.config['ADMIN_USERNAME'] = DB_USER
    app.config['ADMIN_PASSWORD'] = DB_PASSWORD

    # Tiempo de expiración de la sesión
    app.permanent_session_lifetime = timedelta(minutes=15)

    # Inicializar CSRF Protection
    csrf = CSRFProtect()
    csrf.init_app(app)

    # Inicializar extensión SQLAlchemy
    db.init_app(app)

    # Crear tablas automáticamente si no existen
    with app.app_context():
        from . import routes
        db.create_all()

    return app