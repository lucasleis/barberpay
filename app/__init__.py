from flask import Flask
from flask_wtf import CSRFProtect
from flask_wtf.csrf import generate_csrf
from flask_cors import CORS
from flask_mail import Mail
from .models import db
import os
from datetime import timedelta
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from dotenv import load_dotenv


# ==============================
# Crear la base de datos y tablas si no existen
# ==============================

def ensure_database_and_tables():
    load_dotenv() 

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

        ALTER TABLE barberos
        ADD COLUMN IF NOT EXISTS email VARCHAR(254);

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
                
        ALTER TABLE servicios
        ADD COLUMN IF NOT EXISTS duracion_minutos INTEGER NOT NULL DEFAULT 30;

                
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
                
        ALTER TABLE membresias ADD COLUMN IF NOT EXISTS dni VARCHAR(20);

                             
        CREATE TABLE IF NOT EXISTS membresias (
            id SERIAL PRIMARY KEY,
            id_usuario INTEGER UNIQUE,  -- clientes antiguos
            dni VARCHAR(20),            -- clientes nuevos (puede ser NULL)
            tipo_membresia_id INTEGER NOT NULL REFERENCES tipos_membresia(id),
            usos_disponibles INTEGER NOT NULL,
            fecha_compra TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            peluqueria_id INTEGER NOT NULL REFERENCES peluquerias(id) ON DELETE CASCADE,
            active BOOLEAN DEFAULT TRUE,
            UNIQUE (dni, peluqueria_id)
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
                
        CREATE TABLE IF NOT EXISTS usuario (
            id SERIAL PRIMARY KEY,
            username VARCHAR(80) NOT NULL UNIQUE,
            password VARCHAR(200) NOT NULL,
            salon_id INTEGER,
            rol VARCHAR(20) NOT NULL
        );
                
        CREATE TABLE IF NOT EXISTS clientes (
            id SERIAL PRIMARY KEY,
            nombre VARCHAR(100) NOT NULL,
            apellido VARCHAR(100) NOT NULL,
            email VARCHAR(100),
            dni VARCHAR(20),
            telefono VARCHAR(20),
            peluqueria_id INTEGER NOT NULL REFERENCES peluquerias(id) ON DELETE CASCADE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );

                
        CREATE TABLE IF NOT EXISTS turnos_clientes (
            id SERIAL PRIMARY KEY,
            cliente_id INTEGER NOT NULL REFERENCES clientes(id),
            barber_id INTEGER NOT NULL REFERENCES barberos(id),
            service_id INTEGER NOT NULL REFERENCES servicios(id),
            peluqueria_id INTEGER NOT NULL REFERENCES peluquerias(id) ON DELETE CASCADE,

            fecha DATE NOT NULL,
            hora_inicio TIME NOT NULL,
            duracion_minutos INTEGER NOT NULL,
            hora_fin TIME GENERATED ALWAYS AS (hora_inicio + make_interval(mins => duracion_minutos)) STORED,

            estado TEXT CHECK (estado IN ('pendiente', 'confirmado', 'cancelado')) DEFAULT 'pendiente',
            notas TEXT,
            precio_aplicado NUMERIC(10,2)
        );

        CREATE TABLE IF NOT EXISTS pagos_barberos (
            id SERIAL PRIMARY KEY,
            peluqueria_id INTEGER NOT NULL REFERENCES peluquerias(id) ON DELETE CASCADE,
            barber_id INTEGER NOT NULL REFERENCES barberos(id),
            fecha_inicio_periodo DATE NOT NULL,
            fecha_fin_periodo DATE NOT NULL,
            fecha_pago TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
            monto_periodo NUMERIC(10, 2) NOT NULL,
            monto_descuento NUMERIC(10, 2) DEFAULT 0,
            justificacion_descuento TEXT,
            monto_agregado NUMERIC(10, 2) DEFAULT 0,
            justificacion_agregado TEXT,
            monto_final NUMERIC(10, 2) NOT NULL,
            metodo_transferencia NUMERIC(10, 2) DEFAULT 0,
            metodo_efectivo NUMERIC(10, 2) DEFAULT 0
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

csrf = CSRFProtect()
mail = Mail()

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

    # Configuración Flask-Mail (SMTP)
    # Para Gmail necesitás una App Password, no la contraseña real.
    # Ver: https://support.google.com/accounts/answer/185833
    app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
    app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'true').lower() == 'true'
    app.config['MAIL_USE_SSL'] = os.environ.get('MAIL_USE_SSL', 'false').lower() == 'true'
    app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = (
        os.environ.get('MAIL_SENDER_NAME', 'BarberPay'),
        os.environ.get('MAIL_USERNAME', '')
    )

    # Clave secreta para sesiones y CSRF
    app.secret_key = os.environ.get('SECRET_KEY', 'clave_segura_default')
    app.config['ADMIN_USERNAME'] = DB_USER
    app.config['ADMIN_PASSWORD'] = DB_PASSWORD

    # Tiempo de expiración de la sesión
    app.permanent_session_lifetime = timedelta(hours=12)

    # Inicializar CSRF Protection
    #csrf = CSRFProtect()
    csrf.init_app(app)

    # Inicializar Flask-Mail
    mail.init_app(app)

    # Inicializar extensión SQLAlchemy
    db.init_app(app)

    CORS(app, origins=["http://localhost:5173"])  


    # Crear tablas automáticamente si no existen
    with app.app_context():
        from . import routes
        db.create_all()

        # from . import mp_test
        # app.register_blueprint(mp_test.mercadopago_routes)

    @app.template_filter('formato_peso')
    def formato_peso(value):
        try:
            v = float(value or 0)
            if v == int(v):
                formatted = f"{int(v):,}".replace(',', '.')
            else:
                formatted = f"{v:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
            return f"${formatted}"
        except (ValueError, TypeError):
            return f"${value}"

    # Inyectar CSRF token en todos los templates
    @app.context_processor
    def inject_csrf_token():
        return dict(csrf_token=generate_csrf())
    
    @app.after_request
    def set_csrf_cookie(response):
        response.set_cookie('csrf_token', generate_csrf())
        return response

    return app
