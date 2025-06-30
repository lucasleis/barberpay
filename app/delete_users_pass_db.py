from app import create_app
from app.models import db, Usuario

app = create_app()

with app.app_context():
    username = 'barber'  # Cambiá por el nombre que quieras eliminar
    usuario = Usuario.query.filter_by(username=username).first()

    if usuario:
        db.session.delete(usuario)
        db.session.commit()
        print(f"Usuario '{username}' eliminado con éxito.")
    else:
        print(f"Usuario '{username}' no encontrado.")
