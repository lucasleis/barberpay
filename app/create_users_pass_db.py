from app import create_app
from app.models import db, Usuario
from werkzeug.security import generate_password_hash
import os
app = create_app()

with app.app_context():
    nuevo = Usuario(
        username='admin',
        password=generate_password_hash('admin'),
        salon_id=1,
        rol="admin"
    )
    db.session.add(nuevo)
    db.session.commit()
    print("Usuario creado con éxito.")
