from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from enum import Enum

db = SQLAlchemy()

class PaymentMethodEnum(Enum):
    CASH = 'Efectivo'
    TRANSFER = 'Transferencia'
    CARD = 'Tarjeta'

class Barber(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    active = db.Column(db.Boolean, default=True)

class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    price = db.Column(db.Float)

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    barber_id = db.Column(db.Integer, db.ForeignKey('barber.id'))
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'))
    barber = db.relationship('Barber')
    service = db.relationship('Service')

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointment.id'))
    amount = db.Column(db.Float)
    method = db.Column(db.Enum(PaymentMethodEnum))
    appointment = db.relationship('Appointment')
