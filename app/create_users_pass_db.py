from app import create_app
from app.models import db, Usuario
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    nuevo = Usuario(
        username='barber',
        password=generate_password_hash('barber'),
        salon_id=1
    )
    db.session.add(nuevo)
    db.session.commit()
    print("Usuario creado con éxito.")
