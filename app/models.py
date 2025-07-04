from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
# from backports.zoneinfo import ZoneInfo
from zoneinfo import ZoneInfo
from sqlalchemy import CheckConstraint

db = SQLAlchemy()

### Funciones Auxiliares

def now_buenos_aires():
    return datetime.now(ZoneInfo("America/Argentina/Buenos_Aires"))


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


class MetodoPago(db.Model):
    __tablename__ = 'metodos_pago'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), unique=True, nullable=False)
    active = db.Column(db.Boolean, default=True)
    peluqueria_id = db.Column(db.Integer, db.ForeignKey('peluquerias.id'), nullable=False)


class Servicio(db.Model):
    __tablename__ = 'servicios'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    peluqueria_id = db.Column(db.Integer, db.ForeignKey('peluquerias.id'), nullable=False)
    active = db.Column(db.Boolean, default=True)
    precio = db.Column(db.Float, nullable=False)
    precio_amigo = db.Column(db.Integer)
    precio_descuento = db.Column(db.Integer)
    

class Producto(db.Model):
    __tablename__ = 'productos'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    precio = db.Column(db.Float, nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    peluqueria_id = db.Column(db.Integer, db.ForeignKey('peluquerias.id'), nullable=False)
    comision_empleado = db.Column(db.Float, nullable=False, default=1.0)
    active = db.Column(db.Boolean, default=True)

    __table_args__ = (
        CheckConstraint('comision_empleado >= 1 AND comision_empleado <= 100', name='check_comision_empleado_range'),
    )


class TipoMembresia(db.Model):
    __tablename__ = 'tipos_membresia'
    id = db.Column(db.Integer, primary_key=True)
    peluqueria_id = db.Column(db.Integer, db.ForeignKey('peluquerias.id', ondelete="CASCADE"), nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    precio = db.Column(db.Numeric(10, 2), nullable=False)
    usos = db.Column(db.Integer, nullable=False)
    active = db.Column(db.Boolean, default=True)  
    servicio_id = db.Column(db.Integer, db.ForeignKey('servicios.id'))

    peluqueria = db.relationship('Peluqueria', backref=db.backref('tipos_membresia', lazy=True))


class Membresia(db.Model):
    __tablename__ = 'membresias'

    id = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, unique=True) 
    tipo_membresia_id = db.Column(db.Integer, db.ForeignKey('tipos_membresia.id'), nullable=False)
    usos_disponibles = db.Column(db.Integer, nullable=False)
    fecha_compra = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    peluqueria_id = db.Column(db.Integer, db.ForeignKey('peluquerias.id', ondelete="CASCADE"), nullable=False)
    active = db.Column(db.Boolean, default=True)

    tipo_membresia = db.relationship('TipoMembresia', backref=db.backref('membresias', lazy=True))
    peluqueria = db.relationship('Peluqueria', backref=db.backref('membresias', lazy=True))


class AppointmentTurno(db.Model):
    __tablename__ = 'productos_turno'
    id = db.Column(db.Integer, primary_key=True)
    turno_id = db.Column(db.Integer, db.ForeignKey('turnos.id', ondelete='CASCADE'), nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.Float, nullable=False)

    producto = db.relationship('Producto')
    turno = db.relationship('Appointment', back_populates='productos_turno')


class Appointment(db.Model):
    __tablename__ = 'turnos'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=now_buenos_aires)
    barber_id = db.Column(db.Integer, db.ForeignKey('barberos.id'))
    service_id = db.Column(db.Integer, db.ForeignKey('servicios.id'))
    membresia_id = db.Column(db.Integer, db.ForeignKey('membresias.id'))
    peluqueria_id = db.Column(db.Integer, db.ForeignKey('peluquerias.id'), nullable=False)

    tipo_precio_servicio = db.Column(db.String, nullable=False)  # 'comun', 'amigo', 'descuento'
    #precio_aplicado = db.Column(db.Numeric(10, 2), nullable=False)

    # Relaciones
    barber = db.relationship('Empleado')
    service = db.relationship('Servicio')
    membresia = db.relationship('Membresia')
    productos_turno = db.relationship('AppointmentTurno', back_populates='turno', cascade="all, delete-orphan")


class Pago(db.Model):
    __tablename__ = 'pagos'
    
    id = db.Column(db.Integer, primary_key=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey('turnos.id'), nullable=False)      # en esta var guarda id de servicios, productos o membresia  
    # puede ser NULL si sólo se compra membresía

    membresia_comprada_id = db.Column(db.Integer, db.ForeignKey('membresias.id'), nullable=True)

    payment_method1_id = db.Column(db.Integer, db.ForeignKey('metodos_pago.id'), nullable=False)
    payment_method2_id = db.Column(db.Integer, db.ForeignKey('metodos_pago.id'), nullable=True)
    
    amount_method1 = db.Column(db.Float, nullable=False)
    amount_method2 = db.Column(db.Float, nullable=False)
    amount_tip = db.Column(db.Float, nullable=True)
    
    date = db.Column(db.DateTime, default=now_buenos_aires)
    peluqueria_id = db.Column(db.Integer, db.ForeignKey('peluquerias.id'), nullable=False)

    # Relaciones
    appointment = db.relationship('Appointment')
    method1 = db.relationship('MetodoPago', foreign_keys=[payment_method1_id])
    method2 = db.relationship('MetodoPago', foreign_keys=[payment_method2_id])
    membresia_comprada = db.relationship('Membresia')


class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)  # almacena el hash
    salon_id = db.Column(db.Integer) 
    rol = db.Column(db.String(20), nullable=False)  
