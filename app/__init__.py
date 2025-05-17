from flask import Flask
from .models import db
import os

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///barber.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    app.secret_key = 'alguna_clave_secreta_segura'  # Reemplazala por algo más seguro
    app.config['ADMIN_USERNAME'] = 'admin'
    app.config['ADMIN_PASSWORD'] = 'secret' 

    db.init_app(app)

    with app.app_context():
        from . import routes
        db.create_all()

    return app
