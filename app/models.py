from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Peluqueria(db.Model):
    __tablename__ = 'peluquerias'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    direccion = db.Column(db.Text)
    telefono = db.Column(db.String(20))

    barber = db.relationship('Empleado', backref='peluqueria', cascade="all, delete")
    service = db.relationship('Servicio', backref='peluqueria', cascade="all, delete")
    turnos = db.relationship('Appointment', backref='peluqueria', cascade="all, delete")
    metodos_pago = db.relationship('MetodoPago', backref='peluqueria', cascade="all, delete")
    pagos = db.relationship('Pago', backref='peluqueria', cascade="all, delete")


class Empleado(db.Model):
    __tablename__ = 'barberos'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    active = db.Column(db.Boolean, default=True)
    porcentaje = db.Column(db.Integer, nullable=False)
    peluqueria_id = db.Column(db.Integer, db.ForeignKey('peluquerias.id'), nullable=False)


class Servicio(db.Model):
    __tablename__ = 'servicios'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    precio = db.Column(db.Float, nullable=False)
    peluqueria_id = db.Column(db.Integer, db.ForeignKey('peluquerias.id'), nullable=False)


class Producto(db.Model):
    __tablename__ = 'productos'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    precio = db.Column(db.Float, nullable=False)
    peluqueria_id = db.Column(db.Integer, db.ForeignKey('peluquerias.id'), nullable=False)


class Appointment(db.Model):
    __tablename__ = 'turnos'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    barber_id = db.Column(db.Integer, db.ForeignKey('barberos.id'))
    service_id = db.Column(db.Integer, db.ForeignKey('servicios.id'))
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'))
    peluqueria_id = db.Column(db.Integer, db.ForeignKey('peluquerias.id'), nullable=False)

    barber = db.relationship('Empleado')
    service = db.relationship('Servicio')


class MetodoPago(db.Model):
    __tablename__ = 'metodos_pago'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), unique=True, nullable=False)
    active = db.Column(db.Boolean, default=True)
    peluqueria_id = db.Column(db.Integer, db.ForeignKey('peluquerias.id'), nullable=False)


class Pago(db.Model):
    __tablename__ = 'pagos'
    
    id = db.Column(db.Integer, primary_key=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey('turnos.id'), nullable=False)      # en esta var guarda id de servicios y productos  
    
    payment_method1_id = db.Column(db.Integer, db.ForeignKey('metodos_pago.id'), nullable=False)
    payment_method2_id = db.Column(db.Integer, db.ForeignKey('metodos_pago.id'), nullable=True)
    
    amount_method1 = db.Column(db.Float, nullable=False)
    amount_method2 = db.Column(db.Float, nullable=False)
    amount_tip = db.Column(db.Float, nullable=True)
    
    date = db.Column(db.DateTime, default=datetime.utcnow)
    peluqueria_id = db.Column(db.Integer, db.ForeignKey('peluquerias.id'), nullable=False)

    # Relaciones
    appointment = db.relationship('Appointment')
    method1 = db.relationship('MetodoPago', foreign_keys=[payment_method1_id])
    method2 = db.relationship('MetodoPago', foreign_keys=[payment_method2_id])

