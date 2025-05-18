from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Peluqueria(db.Model):
    __tablename__ = 'peluquerias'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    direccion = db.Column(db.Text)
    telefono = db.Column(db.String(20))

    barberos = db.relationship('Barber', backref='peluqueria', cascade="all, delete")
    servicios = db.relationship('Service', backref='peluqueria', cascade="all, delete")
    turnos = db.relationship('Appointment', backref='peluqueria', cascade="all, delete")
    metodos_pago = db.relationship('PaymentMethod', backref='peluqueria', cascade="all, delete")
    pagos = db.relationship('Payment', backref='peluqueria', cascade="all, delete")


class Empleado(db.Model):
    __tablename__ = 'barberos'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    active = db.Column(db.Boolean, default=True)
    peluqueria_id = db.Column(db.Integer, db.ForeignKey('peluquerias.id'), nullable=False)


class Servicio(db.Model):
    __tablename__ = 'servicios'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    peluqueria_id = db.Column(db.Integer, db.ForeignKey('peluquerias.id'), nullable=False)


class Appointment(db.Model):
    __tablename__ = 'turnos'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    barber_id = db.Column(db.Integer, db.ForeignKey('barberos.id'))
    service_id = db.Column(db.Integer, db.ForeignKey('servicios.id'))
    peluqueria_id = db.Column(db.Integer, db.ForeignKey('peluquerias.id'), nullable=False)

    barber = db.relationship('Barber')
    service = db.relationship('Service')


class MetodoPago(db.Model):
    __tablename__ = 'metodos_pago'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    active = db.Column(db.Boolean, default=True)
    peluqueria_id = db.Column(db.Integer, db.ForeignKey('peluquerias.id'), nullable=False)


class Pago(db.Model):
    __tablename__ = 'pagos'
    id = db.Column(db.Integer, primary_key=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey('turnos.id'))
    amount = db.Column(db.Float, nullable=False)
    payment_method_id = db.Column(db.Integer, db.ForeignKey('metodos_pago.id'))
    date = db.Column(db.DateTime, default=datetime.utcnow)
    peluqueria_id = db.Column(db.Integer, db.ForeignKey('peluquerias.id'), nullable=False)

    appointment = db.relationship('Appointment')
    method = db.relationship('PaymentMethod')
