from flask import Flask 
from .models import db
import os
from datetime import timedelta

def create_app():
    app = Flask(__name__)

    # Configuración de la base de datos PostgreSQL desde variables de entorno
    DB_NAME = os.environ.get('DB_NAME', 'peluquerias')
    DB_USER = os.environ.get('DB_USER', 'admin')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', 'admin123')
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_PORT = os.environ.get('DB_PORT', '5432')

    # app.config['SQLALCHEMY_DATABASE_URI'] = (
    #     f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
    # )
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///peluquerias.db'

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Clave secreta para sesiones y credenciales admin para login simple
    app.secret_key = os.environ.get('SECRET_KEY', 'clave_segura_default')
    app.config['ADMIN_USERNAME'] = DB_USER
    app.config['ADMIN_PASSWORD'] = DB_PASSWORD

    # Tiempo de expiración de la sesión (por ejemplo, 15 minutos)
    app.permanent_session_lifetime = timedelta(minutes=15)

    # Inicializar extensión SQLAlchemy
    db.init_app(app)

    # Crear tablas automáticamente si no existen
    with app.app_context():
        from . import routes  # importa rutas (si las tenés)
        db.create_all()

    return app
