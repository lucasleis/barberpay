from flask import current_app as app, render_template, request, redirect, url_for, session, flash, jsonify, Blueprint
from . import db
from . import csrf
from .models import Empleado, Servicio, MetodoPago, Pago, Appointment, Producto, Membresia, TipoMembresia, AppointmentTurno, Usuario, TurnoCliente, Cliente
from .auth import login_required
from sqlalchemy import desc, text, case
from sqlalchemy.sql import extract, func
from sqlalchemy.orm import aliased, selectinload, joinedload
from datetime import datetime, timedelta, time, date
from dateutil.relativedelta import relativedelta
from collections import defaultdict
# from backports.zoneinfo import ZoneInfo
from zoneinfo import ZoneInfo
from decimal import Decimal
import logging
from werkzeug.security import check_password_hash
from functools import wraps
from werkzeug.security import generate_password_hash

from app.models import now_buenos_aires


# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


# Funciones auxiliares

def get_payment_page_data(salon_id):
    MetodoPago1 = aliased(MetodoPago)
    MetodoPago2 = aliased(MetodoPago)

    hoy = datetime.today().date()
    inicio_dia = datetime.combine(hoy, time.min)
    fin_dia = datetime.combine(hoy, time.max)

    pagos_query = (
        db.session.query(Pago)
        .join(Pago.appointment)
        .join(Appointment.barber)
        .outerjoin(Appointment.service)
        .outerjoin(Appointment.productos_turno)
        .join(MetodoPago1, Pago.payment_method1_id == MetodoPago1.id)
        .outerjoin(MetodoPago2, Pago.payment_method2_id == MetodoPago2.id)
        .filter(
            Pago.peluqueria_id == salon_id,
            Pago.date >= inicio_dia,
            Pago.date <= fin_dia
        )
        .options(
            selectinload(Pago.appointment)
                .selectinload(Appointment.productos_turno)
                .joinedload(AppointmentTurno.producto)
        )
        .add_entity(MetodoPago1)
        .add_entity(MetodoPago2)
        .order_by(Pago.date.desc())
        .all()
    )

    pagos_data = []
    for pago, method1, method2 in pagos_query:
        pago.method1 = method1
        pago.method2 = method2
        pagos_data.append(pago)

    barbers = Empleado.query.filter_by(active=True, peluqueria_id=salon_id).all()
    services = Servicio.query.filter_by(active=True, peluqueria_id=salon_id).all()
    methods = MetodoPago.query.filter_by(active=True, peluqueria_id=salon_id).all()

    return pagos_data, barbers, services, methods

def calcular_pagos_entre_fechas(start_date, end_date):

    pagos = Pago.query.options(
        joinedload(Pago.appointment).joinedload(Appointment.productos_turno).joinedload(AppointmentTurno.producto),
        joinedload(Pago.appointment).joinedload(Appointment.barber),
        joinedload(Pago.appointment).joinedload(Appointment.service),
        joinedload(Pago.membresia_comprada).joinedload(Membresia.tipo_membresia),
        joinedload(Pago.appointment).joinedload(Appointment.membresia).joinedload(Membresia.tipo_membresia),
        joinedload(Pago.method1),
        joinedload(Pago.method2)
    ).filter(Pago.date >= start_date, Pago.date <= end_date).order_by(desc(Pago.date)).all()
    
    total_general = 0
    total_propietario = 0
    total_por_empleado = defaultdict(lambda: {"monto": 0, "cortes": 0, "monto_cortes":0, "productos":0, "monto_productos":0, "propinas": 0})
    total_por_metodo_pago = defaultdict(float)
    monto_servicio = Decimal('0')
    pago_empleado = Decimal('0')
    pago_empleado_servicio = Decimal('0')
    pago_empleado_producto = Decimal('0')

    lista_pagos = []

    for pago in pagos:
        pago_dict = {
            "fecha": pago.date.strftime('%d-%m'),
            "empleado": "",
            "porcentaje_empleado": 0,
            "servicio": "",
            "valor_servicio": 0,
            "producto": "",
            "valor_producto": 0,
            "membresia": "",
            "valor_membresia": 0,
            "metodo_pago": [],
            "monto": (pago.amount_method1 or 0) + (pago.amount_method2 or 0),
            "propina": pago.amount_tip or 0,
            "pago_empleado": 0,
            "pago_propietario": 0,
        }

        empleado = None
        porcentaje = 0
        productos_nombres = []
        montos_productos = []
        porcentajes_productos = []
        pago_empleado_productos = 0
        total_propietarios_productos = 0
  
        if pago.appointment and pago.appointment.service:
            pago_propietario_servicio = 0

            servicio = pago.appointment.service
            tipo_precio = pago.appointment.tipo_precio_servicio

            empleado = pago.appointment.barber
            
            monto_servicio = servicio.precio
            porcentaje_servicio = empleado.porcentaje
            pago_empleado_servicio = (monto_servicio * porcentaje_servicio) / 100
            pago_propietario_servicio = float(monto_servicio - pago_empleado_servicio)

            if tipo_precio == 'comun':
                # monto_servicio = servicio.precio
                servicio_name = servicio.name
            elif tipo_precio == 'amigo':
                monto_servicio = servicio.precio_amigo
                servicio_name = "Vale por Corte"
                pago_propietario_servicio = 0
            elif tipo_precio == 'descuento':
                monto_servicio = servicio.precio_descuento
                servicio_name = servicio.name + " Descuento"
                diferencia_servicio = pago_propietario_servicio - (float(servicio.precio) - float(servicio.precio_descuento))
                pago_propietario_servicio = float(diferencia_servicio)
                print(f"pago_propietario_servicio: ",pago_propietario_servicio)
                
            else:
                monto_servicio = 0

            total_por_empleado[empleado.name]["monto"] += float(pago_empleado_servicio)
            total_por_empleado[empleado.name]["monto_cortes"] += float(pago_empleado_servicio)
            total_por_empleado[empleado.name]["cortes"] += 1

            if not pago.appointment.productos_turno:        

                pago_dict.update({
                    "empleado": empleado.name,
                    "porcentaje_empleado": porcentaje_servicio,
                    "servicio": servicio_name,
                    "valor_servicio": monto_servicio,
                    "monto": (pago.amount_method1 or 0) + (pago.amount_method2 or 0),
                    "pago_empleado": pago_empleado_servicio,
                    "pago_propietario": pago_propietario_servicio
                })

            if tipo_precio == 'amigo':
                total_propietario -= pago_empleado_servicio
                pago_propietario_servicio = -pago_propietario_servicio
                # print("total_por_empleado[empleado.name]['monto']: ",total_por_empleado[empleado.name]["monto"])

            total_propietario += float(pago_propietario_servicio)
            total_general += float(monto_servicio)

        if pago.appointment and pago.appointment.productos_turno:
            for pt in pago.appointment.productos_turno:
                producto = pt.producto
                monto_producto = pt.precio_unitario * pt.cantidad
                porcentaje_producto = float(producto.comision_empleado)
                empleado = pago.appointment.barber
                pago_empleado_producto = (monto_producto * porcentaje_producto) / 100

                productos_nombres.append(producto.name + " (" + str(pt.cantidad)+")")
                montos_productos.append(monto_producto)
                porcentajes_productos.append(porcentaje_producto)
                pago_empleado_productos += float(pago_empleado_producto) 

                total_por_empleado[empleado.name]["monto"] += float(pago_empleado_producto)
                total_por_empleado[empleado.name]["productos"] += float(pt.cantidad)
                total_por_empleado[empleado.name]["monto_productos"] += float(pago_empleado_producto)

                total_propietarios_productos += float(monto_producto - pago_empleado_producto) 
                total_propietario += float(monto_producto - pago_empleado_producto)
                total_general += float(monto_producto)

            if not pago.appointment.service:

                pago_dict.update({
                    "empleado": empleado.name,
                    "porcentaje_empleado": porcentajes_productos if len(porcentajes_productos) > 1 else porcentajes_productos[0],
                    "producto": productos_nombres,
                    "montos_productos": montos_productos,
                    "pago_empleado": float(pago_empleado_productos),
                    "pago_propietario": total_propietarios_productos
                })

        if pago.appointment and pago.appointment.service and pago.appointment.productos_turno:
            porcentajes_productos = [str(porcentaje_servicio)] + porcentajes_productos

            pago_dict.update({
                "empleado": empleado.name,
                "porcentaje_empleado": porcentajes_productos,
                "servicio": servicio_name,
                "valor_servicio": monto_servicio,
                "producto": productos_nombres,
                "montos_productos": montos_productos,
                "pago_empleado": float(pago_empleado_servicio) + float(pago_empleado_productos),
                "pago_propietario": float(pago_propietario_servicio) + float(total_propietarios_productos)
                #"pago_propietario": float(Decimal(monto_servicio) - Decimal(pago_empleado_servicio)) + float(Decimal(monto_producto) - Decimal(pago_empleado_producto))
            })
            # total_por_empleado[empleado.name]["monto"] += float(pago_empleado_servicio)+ float(pago_empleado_producto)
            # total_por_empleado[empleado.name]["monto_cortes"] += float(pago_empleado_servicio)
            # total_por_empleado[empleado.name]["monto_productos"] += float(pago_empleado_producto)
            # total_por_empleado[empleado.name]["cortes"] += 1
            # total_por_empleado[empleado.name]["productos"] += float(pt.cantidad)
            # total_propietario += float(monto_servicio - pago_empleado_servicio) +float(monto_producto - pago_empleado_producto)
            # total_propietario += (float(monto_servicio) - float(pago_empleado_servicio)) + (float(monto_producto) - float(pago_empleado_producto))
            # total_general += float(monto_servicio) + float(monto_producto)

        if pago.membresia_comprada:
            empleado = pago.appointment.barber
            tipo = pago.membresia_comprada.tipo_membresia
            monto = float(tipo.precio)
            pago_dict.update({
                "empleado": empleado.name,
                "membresia": tipo.nombre,
                "valor_membresia": monto,
                "pago_empleado": 0,
                "pago_propietario": monto,
            })
            total_propietario += monto
            total_general += monto

        elif pago.appointment and pago.appointment.membresia:
            tipo = pago.appointment.membresia.tipo_membresia
            empleado = pago.appointment.barber
            porcentaje = empleado.porcentaje
            # monto = float(tipo.precio) / tipo.usos
            servicio = Servicio.query.get(tipo.servicio_id)
            monto = servicio.precio if servicio else 0

            pago_empleado = (monto * porcentaje) / 100
            pago_propietario = 0
            if pago.appointment.productos_turno:
                pago_empleado += float(pago_empleado_producto)
                pago_propietario = float(Decimal(monto_producto) - Decimal(pago_empleado_producto))

            pago_dict.update({
                "empleado": empleado.name,
                "porcentaje_empleado": porcentaje,
                "membresia": tipo.nombre + " (uso)",
                "valor_membresia": monto,
                "pago_empleado": pago_empleado,
                "pago_propietario": pago_propietario,
            })

            total_por_empleado[empleado.name]["monto"] += float(pago_empleado)
            total_por_empleado[empleado.name]["monto_cortes"] += float(pago_empleado)
            total_por_empleado[empleado.name]["cortes"] += 1
            total_propietario -= float(pago_empleado)

        if pago.amount_tip and empleado:
            total_por_empleado[empleado.name]["propinas"] += pago.amount_tip
            total_general += pago.amount_tip

        metodos_pago_str = ""

        if pago.method1:
            if (pago.appointment and pago.appointment.service) and not (pago.appointment.service):
                tipo_precio = pago.appointment.tipo_precio_servicio
                # monto_metodo1 = pago.amount_method1 or 0
                if tipo_precio == 'amigo':
                    total_por_metodo_pago[pago.method1.nombre] += 0
                    if pago.amount_tip != 0:
                        pago_dict["metodo_pago"].append(pago.method1.nombre)
                        total_por_metodo_pago[pago.method1.nombre] += pago.amount_tip
                        metodos_pago_str = "$" + "{:,.0f}".format(pago.amount_method1).replace(",", ".")
                    else: 
                        pago_dict["metodo_pago"].append("-")
                        metodos_pago_str = "$0"
                else: 
                    total_por_metodo_pago[pago.method1.nombre] += pago.amount_method1 or 0
                    pago_dict["metodo_pago"].append(pago.method1.nombre)
                    # metodos_pago_str = "$"+str(int(pago.amount_method1))
                    metodos_pago_str = "$" + "{:,.0f}".format(pago.amount_method1).replace(",", ".")
            else:
                total_por_metodo_pago[pago.method1.nombre] += pago.amount_method1 or 0
                pago_dict["metodo_pago"].append(pago.method1.nombre)
                # metodos_pago_str = "$"+str(int(pago.amount_method1))
                metodos_pago_str = "$" + "{:,.0f}".format(pago.amount_method1).replace(",", ".")

        if pago.method2:
            total_por_metodo_pago[pago.method2.nombre] += pago.amount_method2 or 0
            # metodos_pago_str += " - $"+str(int(pago.amount_method2))
            if pago.amount_method2 > 0:
                pago_dict["metodo_pago"].append(pago.method2.nombre)
                metodos_pago_str += " - $" + "{:,.0f}".format(pago.amount_method2).replace(",", ".")

        pago_dict["metodos_pago_str"] = metodos_pago_str

        lista_pagos.append(pago_dict)

    return {
        "pagos": lista_pagos,
        "totales": {
            "monto_total": total_general,
            "propietario_total": total_propietario,
            "empleados": total_por_empleado,
            "metodos_pago": total_por_metodo_pago,
            "forma_metodos_pagos": "",
        }
    }


@app.template_filter('moneda')
def moneda(valor):
    try:
        valor_int = int(round(float(valor)))
        return f"${valor_int:,}".replace(",", ".")
    except (ValueError, TypeError):
        return "$0"

@app.template_filter('miles')
def miles(valor):
    try:
        valor_int = int(round(float(valor)))
        return f"{valor_int:,}".replace(",", ".")
    except (ValueError, TypeError):
        return "0"

def obtener_id_usuario_disponible(peluqueria_id):
    # Obtener todos los id_usuario y los id existentes en esa peluquería
    ids = db.session.query(Membresia.id).filter_by(peluqueria_id=peluqueria_id).all()
    id_usuarios = db.session.query(Membresia.id_usuario).filter_by(peluqueria_id=peluqueria_id).all()

    usados_set = set()
    usados_set.update(r[0] for r in ids if r[0] is not None)
    usados_set.update(r[0] for r in id_usuarios if r[0] is not None)

    # Buscar el menor número entero libre
    i = 1
    while i in usados_set:
        i += 1

    return i


@app.context_processor
def inject_logo():
    dominio = request.host

    logos_por_dominio = {
        'barbacompany.com.ar': './static/Barba&Co_logo.png',
    }

    return {
        'logo_url': logos_por_dominio.get(dominio, '')  # Retorna vacío si no está
    }

### Administrador ###

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            # Guarda la URL original a la que intentaba acceder
            return redirect(url_for('login', next=request.path))
        return f(*args, **kwargs)
    return decorated_function

"""
    @app.route('/login', methods=['GET', 'POST'])
    def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if (username == app.config['ADMIN_USERNAME'] and
            password == app.config['ADMIN_PASSWORD']):
            session.permanent = True
            session['user'] = username
            session['salon_id'] = 1 
            return redirect(url_for('dashboard'))
        else:
            flash("Usuario o contraseña incorrectos.")
            return redirect(url_for("login"))

    if "user" in session:
        return redirect(url_for("dashboard"))

    return render_template('login.html')
"""
@app.route('/login', methods=['GET', 'POST'])
def login():
    next_page = request.args.get('next')

    # i el usuario ya está en sesión, redirigir directamente
    if 'user' in session:
        if session.get('rol') == 'admin':
            return redirect(next_page or url_for('dashboard'))
        else:
            return redirect(next_page or url_for('add_payment'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        usuario = Usuario.query.filter_by(username=username).first()

        if usuario and check_password_hash(usuario.password, password):
            session.permanent = True
            session['user'] = usuario.username
            session['salon_id'] = usuario.salon_id
            session['rol'] = usuario.rol

            if usuario.rol == 'admin':
                return redirect(next_page or url_for('dashboard'))
            else:
                return redirect(next_page or url_for('add_payment'))

        else:
            flash("Usuario o contraseña incorrectos.", "danger")
            return redirect(url_for("login", next=next_page))

    return render_template('login.html')

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route('/dashboard')
@login_required
def dashboard():
    if session.get("rol") != "admin":
        flash("Acceso denegado. Solo el administrador puede acceder al panel.", "danger")
        return redirect(url_for("login"))

    return render_template('dashboard.html')


"""
@app.route('/clientes')
def get_clientes():
    clientes = Cliente.query.filter_by(active=True).all()  # suponiendo que tienes un modelo Cliente
    return jsonify([
        {
            "id": c.id,
            "nombre": c.nombre,
            "telefono": c.telefono,
            "email": c.email,
            "active": c.active
        }
        for c in clientes
    ])
"""

### Empleados ###

@app.route('/barbers')
def get_barbers():
    barberos = Empleado.query.filter_by(active=True).all()
    return jsonify([
        {
            "id": b.id,
            "name": b.name,
            "active": b.active,
            "porcentaje": b.porcentaje,
            "peluqueria_id": b.peluqueria_id
        }
        for b in barberos
    ])


@app.route('/admin/barbers')
def list_barbers():
    if "user" not in session:
        return redirect(url_for("login", next=request.path))

    salon_id = session.get('salon_id')
    barbers = Empleado.query.filter_by(active=True, peluqueria_id=salon_id).all()
    return render_template('barbers.html', barbers=barbers)

@app.route('/admin/barbers/add', methods=['POST'])
def add_barber():
    if "user" in session:
        name = request.form['name']
        porcentaje = request.form.get('porcentaje')
        if not porcentaje:
            return "Porcentaje es requerido", 400
        salon_id = session.get('salon_id')
        db.session.add(Empleado(name=name, peluqueria_id=salon_id, porcentaje=porcentaje))
        db.session.commit()
        return redirect(url_for('list_barbers'))
    else:
        return redirect(url_for("login"))

@app.route('/admin/barbers/delete/<int:id>')
def delete_barber(id):
    if "user" in session:
        barber = Empleado.query.get(id)
        barber.active = False
        db.session.commit()
        return redirect(url_for('list_barbers'))
    else:
        return redirect(url_for("login"))

@app.route('/admin/barbers/update/<int:id>', methods=['POST'])
def update_barber(id):
    if "user" not in session:
        return redirect(url_for("login"))

    original = Empleado.query.get_or_404(id)
    original.active = False  

    name = request.form.get('name')
    try:
        porcentaje = float(request.form.get('porcentaje', 0))
    except ValueError:
        porcentaje = 0

    nuevo = Empleado(
        name=name,
        porcentaje=porcentaje,
        peluqueria_id=original.peluqueria_id,
        active=True
    )

    db.session.add(nuevo)
    db.session.commit()

    return redirect(url_for('list_barbers'))


### Servicios ###

@app.route('/services')
def get_services():
    servicios = Servicio.query.filter_by(active=True).all()
    return jsonify([
        {
            "id": s.id,
            "name": s.name,
            "active": s.active,
            "precio": float(s.precio) if s.precio is not None else None,
            "precio_amigo": s.precio_amigo,
            "precio_descuento": s.precio_descuento,
            "peluqueria_id": s.peluqueria_id
        }
        for s in servicios
    ])


@app.route('/admin/services')
def list_services():
    if "user" not in session:
        return redirect(url_for("login", next=request.path))

    salon_id = session.get('salon_id')
    services = Servicio.query.filter_by(active=True, peluqueria_id=salon_id).all()
    return render_template('services.html', services=services)

@app.route('/admin/services/add', methods=['POST'])
def add_service():
    if "user" in session:
        name = request.form.get('name')
        precio = float(request.form.get('precio', 0))

        try:
            precio_descuento = float(request.form.get('precio_descuento', 0) or 0)
        except ValueError:
            precio_descuento = 0

        salon_id = session.get('salon_id')

        db.session.add(Servicio(
            name=name,
            precio=precio,
            precio_amigo=0,
            precio_descuento=precio_descuento,
            peluqueria_id=salon_id
        ))
        db.session.commit()
        return redirect(url_for('list_services'))
    else:
        return redirect(url_for("login"))

@app.route('/admin/services/delete/<int:id>')
def delete_service(id):
    if "user" in session:
        service = Servicio.query.get(id)
        service.active = False
        # db.session.delete(service)
        db.session.commit()
        return redirect(url_for('list_services'))
    else:
        return redirect(url_for("login"))

@app.route('/update_service/<int:id>', methods=['POST'])
def update_service(id):
    if "user" not in session:
        return redirect(url_for("login"))

    # Buscar el servicio original
    original = Servicio.query.get_or_404(id)
    original.active = False

    # Obtener los nuevos valores del formulario
    name = request.form.get('name')
    try:
        precio = float(request.form.get('precio', 0))
    except ValueError:
        precio = 0

    try:
        precio_amigo = float(request.form.get('precio_amigo', 0) or 0)
    except ValueError:
        precio_amigo = 0

    try:
        precio_descuento = float(request.form.get('precio_descuento', 0) or 0)
    except ValueError:
        precio_descuento = 0

    # Crear nuevo servicio con mismos valores
    nuevo = Servicio(
        name=name,
        precio=precio,
        precio_amigo=precio_amigo,
        precio_descuento=precio_descuento,
        peluqueria_id=original.peluqueria_id,
        active=True
    )

    db.session.add(nuevo)
    db.session.commit()

    return redirect(url_for('list_services'))


### Productos ###

@app.route('/admin/products')
def list_products():
    if "user" in session:
        salon_id = session.get('salon_id')
        products = Producto.query.filter_by(active=True, peluqueria_id=salon_id).all()
        return render_template('products.html', products=products)
    else:
        return redirect(url_for("login"))

@app.route('/admin/products/add', methods=['POST'])
def add_product():
    if "user" not in session:
        return redirect(url_for("login"))
    
    name = request.form['name']
    precio = float(request.form['precio'])
    salon_id = session.get('salon_id')
    cantidad = int(request.form['cantidad'])
    comision = float(request.form['comision']) 
    
    # Validar comisión esté entre 1 y 100 (por seguridad)
    if not (1 <= comision <= 100):
        flash("La comisión debe estar entre 1 y 100")
        return redirect(url_for('list_products'))

    nuevo_producto = Producto(
        name=name,
        precio=precio,
        peluqueria_id=salon_id,
        cantidad=cantidad,
        comision_empleado=comision
    )
    db.session.add(nuevo_producto)
    db.session.commit()
    return redirect(url_for('list_products'))
    
@app.route('/admin/products/update_quantity/<int:id>', methods=['POST'])
def update_product_quantity(id):
    if "user" not in session:
        return redirect(url_for("login"))

    salon_id = session.get('salon_id')

    # Buscar el producto por ID y peluquería
    product = Producto.query.filter_by(id=id, peluqueria_id=salon_id).first()

    if not product:
        return "Producto no encontrado o no pertenece al salón", 404

    try:
        product.name = request.form['nombre'].strip()
        product.precio = float(request.form['precio'])
        product.cantidad = int(request.form['cantidad'])
        product.comision_empleado = float(request.form['comision'])

        # Validación extra por seguridad
        if not (1 <= product.comision_empleado <= 100):
            return "Comisión fuera de rango permitido (1-100%)", 400

        db.session.commit()
        return redirect(url_for('list_products'))

    except Exception as e:
        db.session.rollback()
        return f"Error al actualizar el producto: {str(e)}", 400


@app.route('/admin/products/delete/<int:id>')
def delete_product(id):
    if "user" in session:
        product = Producto.query.get(id)
        product.active = False
        # db.session.delete(product)
        db.session.commit()
        return redirect(url_for('list_products'))
    else:
        return redirect(url_for("login"))


### Metodos de Pago ###

@app.route('/admin/payment_methods')
def list_payment_methods():
    if "user" in session:
        methods = MetodoPago.query.filter_by(active=True).all()
        #methods = MetodoPago.query.all()
        return render_template('payment_methods.html', methods=methods)
    else:
        return redirect(url_for("login"))

@app.route('/admin/payment_methods/add', methods=['POST'])
def add_payment_method():
    if "user" in session:
        nombre = request.form['nombre']
        salon_id = session.get('salon_id')
        db.session.add(MetodoPago(nombre=nombre, peluqueria_id=salon_id))
        db.session.commit()
        return redirect(url_for('list_payment_methods'))
    else:
        return redirect(url_for("login"))

@app.route('/admin/payment_methods/delete/<int:id>')
def delete_payment_method(id):
    if "user" in session:
        method = MetodoPago.query.get(id)
        method.active = False
        # db.session.delete(method)
        db.session.commit()
        return redirect(url_for('list_payment_methods'))
    else:
        return redirect(url_for("login"))

@app.route('/admin/payment_methods/update/<int:id>', methods=['POST'])
def update_payment_method(id):
    if "user" in session:
        method = MetodoPago.query.get_or_404(id)
        method.nombre = request.form['nombre']
        db.session.commit()
        return redirect(url_for('list_payment_methods'))
    else:
        return redirect(url_for("login"))


### Tipos de Membresias ###

@app.route('/admin/memberships')
def list_memberships():
    if "user" in session:
        salon_id = session.get('salon_id')
        tipos = TipoMembresia.query.filter_by(active=True, peluqueria_id=salon_id).all()
        servicios = Servicio.query.filter_by(active=True, peluqueria_id=salon_id).all()
        membresias = Membresia.query.filter_by(peluqueria_id=salon_id, active=True).all()
        return render_template('memberships.html', tipos_membresia=tipos, servicios=servicios, membresias=membresias)
    else:
        return redirect(url_for("login"))

@app.route('/admin/memberships/add', methods=['POST'])
def add_membership():
    if "user" in session:
        salon_id = session.get('salon_id')
        nombre = request.form['nombre']
        precio = request.form['precio']
        usos = request.form['cantidad']
        servicio_id = request.form.get('servicio_id')

        nueva = TipoMembresia(
            peluqueria_id=salon_id,
            nombre=nombre,
            precio=precio,
            usos=usos,
            servicio_id=servicio_id 
        )
        db.session.add(nueva)
        db.session.commit()
        return redirect(url_for('list_memberships'))
    else:
        return redirect(url_for("login"))

@app.route('/admin/memberships/delete/<int:id>')
def delete_membership_type(id):
    if "user" in session:
        tipo = TipoMembresia.query.get_or_404(id)
        db.session.delete(tipo)
        db.session.commit()
        return redirect(url_for('list_memberships'))
    else:
        return redirect(url_for("login"))

@app.route('/update_membership_type/<int:id>', methods=['POST'])
def update_membership_type(id):
    if "user" not in session:
        return redirect(url_for("login"))

    original = TipoMembresia.query.get_or_404(id)

    # Desactivar la membresía actual
    original.active = False

    # Crear la nueva membresía con los nuevos datos
    nombre = request.form['nombre']
    precio = float(request.form['precio'])
    usos = int(request.form['usos'])
    servicio_id = int(request.form['servicio_id']) 
    salon_id = original.peluqueria_id

    nueva = TipoMembresia(
        peluqueria_id=salon_id,
        nombre=nombre,
        precio=precio,
        usos=usos,
        servicio_id=servicio_id,  
        active=True
    )

    db.session.add(nueva)
    db.session.commit()
    return redirect(url_for('list_memberships'))


### Membresias ###

@app.route('/membresias/incrementar/<int:id>', methods=['POST'])
def incrementar_usos_membresia(id):
    membresia = Membresia.query.get(id)
    if not membresia:
        return "Membresía no encontrada", 404

    membresia.usos_disponibles += 1
    db.session.commit()
    return "Uso agregado exitosamente", 200

@app.route('/membresias/decrementar/<int:id>', methods=['POST'])
def decrementar_usos_membresia(id):
    membresia = Membresia.query.get(id)
    if not membresia:
        return "Membresía no encontrada", 404

    if membresia.usos_disponibles <= 0:
        return "No hay usos disponibles para descontar", 400

    membresia.usos_disponibles -= 1
    db.session.commit()
    return "Uso descontado exitosamente", 200

@app.route('/admin/memberships/update/<int:membresia_id>', methods=['POST'])
def update_membresia(membresia_id):
    if "user" not in session:
        return redirect(url_for("login"))

    salon_id = session.get('salon_id')
    nueva_id_usuario = request.form.get('id_usuario')
    usos_disponibles = request.form.get('usos_disponibles')

    # Validación básica
    if not nueva_id_usuario or not usos_disponibles:
        flash('Debes completar todos los campos.', 'warning')
        return redirect(url_for('list_memberships'))

    try:
        nueva_id_usuario = int(nueva_id_usuario)
        usos_disponibles = int(usos_disponibles)
    except ValueError:
        flash('Los valores ingresados deben ser numéricos.', 'danger')
        return redirect(url_for('list_memberships'))

    membresia = Membresia.query.filter_by(id=membresia_id, peluqueria_id=salon_id).first()

    if membresia:
        # Verificar que el nuevo id_usuario no esté en uso por otra membresía
        existente = Membresia.query.filter(
            Membresia.id_usuario == nueva_id_usuario,
            Membresia.id != membresia_id,
            Membresia.peluqueria_id == salon_id
        ).first()

        if existente:
            flash(f'El ID de usuario {nueva_id_usuario} ya está en uso.', 'danger')
            return redirect(url_for('list_memberships'))

        membresia.id_usuario = nueva_id_usuario
        membresia.usos_disponibles = usos_disponibles
        try:
            db.session.commit()
            flash('Membresía actualizada correctamente.', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar: {str(e)}', 'danger')
    else:
        flash('Membresía no encontrada.', 'warning')

    return redirect(url_for('list_memberships'))


### Pagos ###

@app.route('/payments/new', methods=['GET', 'POST'])
def add_payment():
    if "user" not in session:
        return redirect(url_for("login", next=request.path))

    #session['salon_id'] = 1
    raw_salon_id = request.form.get("salon_id") or session.get("salon_id")

    try:
        salon_id = int(str(raw_salon_id).strip("{} "))
    except (ValueError, TypeError):
        flash("ID de peluquería inválido.", "danger")
        return redirect(url_for("index"))

    pagos_data, barbers, services, methods = get_payment_page_data(salon_id)
    products = Producto.query.filter_by(active=True, peluqueria_id=salon_id).all()
    membresias = TipoMembresia.query.filter_by(peluqueria_id=session['salon_id'], active=True).all()

    if request.method == 'POST':
        try:
            barber_id = request.form.get('barber_id')
            if not barber_id:
                raise ValueError("Debe seleccionarse un barbero.")

            tip = float(request.form.get('tip') or 0.0)
            toggle_servicio = 'toggle_servicio' in request.form
            toggle_producto = 'toggle_producto' in request.form
            toggle_membresia = 'toggle_membresia' in request.form

            if not toggle_servicio and not toggle_producto and not toggle_membresia:
                raise ValueError("Debe seleccionarse al menos un servicio o producto.")

            # Crear appointment
            appointment = Appointment(
                barber_id=barber_id,
                peluqueria_id=salon_id
            )

            if toggle_servicio:

                check_membresia = request.form.get('membresiaCheckbox') 
                if check_membresia == 'on':

                    membresia_id = request.form.get('check_membresia')
                    if not membresia_id:
                        raise ValueError("Debe seleccionarse un servicio.")
                
                    #membresia = Membresia.query.get(id_usuario=num_membresia)
                    membresia = Membresia.query.filter_by(id_usuario=membresia_id).first()
                    if not membresia:
                        raise ValueError("Membresía no encontrada.")
                    
                    membresia_id = membresia.id
                    appointment.membresia_id = membresia_id

                    if membresia.usos_disponibles <= 0:
                        raise ValueError("No hay usos disponibles para descontar en esta membresía.")

                    membresia.usos_disponibles -= 1
                    db.session.add(membresia)
                    flash(f"Membresía #{membresia.id_usuario}: Quedan {membresia.usos_disponibles} usos disponibles.", "success")

                else:
                    service_id = request.form.get('service_id')
                    if not service_id:
                        raise ValueError("Debe seleccionarse un servicio.")
                    appointment.service_id = service_id
                    
                    if request.form.get('precioDescuentoCheckbox') == 'on':
                        # Obtén el objeto Servicio según el servicio seleccionado en el formulario
                        servicio = Servicio.query.get(service_id)
                        if not servicio:
                            flash('Servicio no encontrado.', 'error')
                            return redirect(url_for('add_payment'))

                        # Valida que exista un precio de descuento
                        if servicio.precio_descuento == 0:
                            flash('Este servicio no tiene precio de descuento disponible.', 'danger')
                            return redirect(url_for('add_payment'))

                        appointment.tipo_precio_servicio = "descuento"
                    elif request.form.get('precioAmigoCheckbox') == 'on':
                        appointment.tipo_precio_servicio = "amigo"
                    else:
                        appointment.tipo_precio_servicio = "comun"

            total_producto = 0.0
            if toggle_producto:
                product_ids = request.form.getlist('product_id[]')
                product_quantities = request.form.getlist('product_quantity[]')
                product_quantities = list(map(int, product_quantities))

                for pid, qty in zip(product_ids, product_quantities):
                    product = Producto.query.get(pid)
                    if not product:
                        raise ValueError(f"Producto con ID {pid} no encontrado.")

                    if product.cantidad < qty:
                        raise ValueError(f"No hay suficiente stock del producto {product.nombre} (stock actual: {product.cantidad})")

                    turno_producto = AppointmentTurno(
                        turno=appointment,
                        producto=product,
                        cantidad=qty,
                        precio_unitario=product.precio
                    )
                    db.session.add(turno_producto)
                    product.cantidad -= qty
                    total_producto += product.precio * qty

            membresia_real = None
            if toggle_membresia:
                membresia_id = request.form.get('membresia_id')
                if not membresia_id:
                    raise ValueError("Debe seleccionarse un servicio.")

                tipo = TipoMembresia.query.get(membresia_id)
                if not tipo:
                    raise ValueError("Tipo de membresía no encontrado.")

                membresia_real = Membresia(
                    tipo_membresia_id=tipo.id,
                    usos_disponibles=tipo.usos,
                    peluqueria_id=salon_id,
                )
                db.session.add(membresia_real)
                db.session.flush()

                # Generar el ID de usuario amigable
                num_disp = obtener_id_usuario_disponible(salon_id)
                membresia_real.id_usuario = num_disp
                print(f"membresia_real.id_usuario = {membresia_real.id_usuario}")

                db.session.flush()  # Se asegura de que membresia_real.id esté disponible

                # ✅ Asignar la FK real (clave primaria, no el id_usuario)
                appointment.membresia_id = membresia_real.id
                print(f"appointment.membresia_id = {appointment.membresia_id}")

            db.session.add(appointment)
            db.session.commit()




            multipagos = 'togglemultiPayment' in request.form

            method_simple_service = int(request.form.get('methodSimple') or 0)
            # amount_simple_service = float(request.form.get('amount_simple') or 0)

            method_multiple_1 = int(request.form.get('method_multiple_1') or 0)
            method_multiple_2 = int(request.form.get('method_multiple_2') or 0)
            amount_method_multi_1 = float(request.form.get('amount_method_multi_1') or 0)
            amount_method_multi_2 = float(request.form.get('amount_method_multi_2') or 0)

            total_real = 0.0
            total_pagado = 0.0

            if toggle_servicio:

                if check_membresia == 'on':
                    total_real = 0 
                else:  
                    precio = request.form.get('servicePrice')
                    precio = precio.split("$")
                    service_price = int(precio[1].replace('.', '') or 0)
                    total_real += service_price

            if toggle_producto:
                total_real += total_producto

            if toggle_membresia:   
                membresia = TipoMembresia.query.get(membresia_id)
                total_real += float(membresia.precio) if membresia else 0

            if multipagos:
                total_real += tip
                if method_multiple_1 == method_multiple_2:
                    flash(f"No se puede repetir el mismo método de pago.")
                    #raise ValueError("No se puede repetir el mismo método de pago.")
                if not method_multiple_1 or not method_multiple_2:
                    raise ValueError("Faltan datos del segundo método de pago.")
                total_pagado = amount_method_multi_1 + amount_method_multi_2
            else:
                if toggle_servicio or toggle_producto or toggle_membresia:
                    total_pagado = total_real + tip
                    total_real += tip
                    
            if abs(total_pagado - total_real) > 0.01:
                # flash(f"El total abonado (${total_pagado}) no coincide con el total real (${total_real}).", "danger")
                raise ValueError(f"El total abonado (${total_pagado}) no coincide con el total real (${total_real}).")

            # Validar que al menos haya un método de pago seleccionado
            if not multipagos:
                if not method_simple_service:
                    flash("Debe seleccionarse al menos un método de pago.", "danger")
                    return redirect(url_for('add_payment'))
            else:
                if not method_multiple_1 or not method_multiple_2:
                    flash("Debe seleccionarse al menos un método de pago en ambas opciones.", "danger")
                    return redirect(url_for('add_payment'))

            pago = Pago(
                appointment_id=appointment.id,
                payment_method1_id=method_simple_service if not multipagos else method_multiple_1,
                payment_method2_id=None if not multipagos else method_multiple_2,
                amount_method1=total_pagado if not multipagos else amount_method_multi_1,
                amount_method2=0 if not multipagos else amount_method_multi_2,
                amount_tip=tip,
                peluqueria_id=salon_id,
                date=datetime.now(ZoneInfo("America/Argentina/Buenos_Aires")),
                membresia_comprada_id=membresia_real.id if membresia_real else None
                #membresia_comprada_id=membresia_real.id_usuario if membresia_real else None
            )

            db.session.add(pago)
            db.session.commit()
            flash("Pago registrado con éxito.", "success")

            if membresia_real:
                flash(f"Numero de membresia: {membresia_real.id_usuario}", "success")

            return redirect(url_for('add_payment'))

        except Exception as e:
            db.session.rollback()
            flash(f"Error al registrar el pago: {str(e)}", "danger")

    return render_template(
        'add_payment.html',
        pagos=pagos_data,
        salon_id=salon_id,
        barbers=barbers,
        services=services,
        methods=methods,
        products=products,
        membresias=membresias
    )


@app.route('/payments/delete/<int:pago_id>', methods=['POST'])
def delete_payment(pago_id):
    #session['salon_id'] = 1
    salon_id = session.get("salon_id")

    pago = Pago.query.get_or_404(pago_id)

    try:
        appointment = Appointment.query.get(pago.appointment_id)

        # Si el turno tenía productos, devolver cantidad al stock
        if appointment and appointment.productos_turno:
            for pt in appointment.productos_turno:
                producto = Producto.query.get(pt.producto_id)
                if producto:
                    producto.cantidad += pt.cantidad  # Devolver al stock
                db.session.delete(pt)  

        # Manejar membresías
        if appointment and appointment.membresia:
            membresia = Membresia.query.get(appointment.membresia_id)
            if membresia:
                # Si el pago era por una membresía comprada (nueva)
                if pago.membresia_comprada_id and pago.membresia_comprada_id == membresia.id:
                    tipo = TipoMembresia.query.get(membresia.tipo_membresia_id)
                    if tipo and membresia.usos_disponibles == tipo.usos:
                        # Nunca fue usada → se puede eliminar
                        db.session.delete(membresia)
                    else:
                        flash("No se puede eliminar la compra de una membresía que ya fue usada.", "warning")
                        return redirect(url_for('add_payment'))
                else:
                    # Si se usó una membresía existente, devolver 1 uso
                    membresia.usos_disponibles += 1

        # Eliminar el pago y el turno
        db.session.delete(pago)
        if appointment:
            db.session.delete(appointment)

        db.session.commit()
        flash("Pago eliminado con éxito.", "success")

    except Exception as e:
        db.session.rollback()
        flash(f"Error al eliminar el pago: {str(e)}", "danger")

    return redirect(url_for('add_payment'))


### Cierres ###

@app.route('/pagos_entre_fechas', methods=['POST'])
def pagos_entre_fechas():
    if "user" not in session:
        return redirect(url_for("login", next=request.path))

    data = request.get_json()
    role = session.get("rol")

    # Definir la zona horaria correcta
    tz = ZoneInfo("America/Argentina/Buenos_Aires")
    
    # Parsear las fechas como naive
    start_date_naive = datetime.fromisoformat(data['start_date'])
    end_date_naive = datetime.fromisoformat(data['end_date'])
    
    # Asignarles la zona horaria correcta
    start_date = start_date_naive.replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=tz)
    end_date = end_date_naive.replace(hour=23, minute=59, second=59, microsecond=999999, tzinfo=tz)

    # start_date = datetime.fromisoformat(data['start_date']).replace(hour=0, minute=0, second=0, microsecond=0)
    # end_date = datetime.fromisoformat(data['end_date']).replace(hour=23, minute=59, second=59, microsecond=999999)
    resultado = calcular_pagos_entre_fechas(start_date, end_date)

    if role != "admin":
        resultado["totales"].pop("propietario_total", None)
        resultado["totales"].pop("monto_total", None)
    
    return jsonify(resultado)

@app.route('/cierres/<int:salon_id>', methods=['GET'])
def cierre_entre_dias(salon_id):
    if "user" not in session:
        return redirect(url_for("login", next=request.path))

    role = session.get("rol")
    today = datetime.today()

    # Calcular el último domingo (inicio de semana)
    last_sunday = today - timedelta(days=today.weekday() + 1 if today.weekday() != 6 else 0)
    last_sunday = last_sunday.replace(hour=0, minute=0, second=0, microsecond=0)
    next_sunday = last_sunday + timedelta(days=7)

    # Estas dos variables se usan para precargar el formulario
    fechaInicio = last_sunday.strftime('%Y-%m-%d')
    fechaFinal = next_sunday.strftime('%Y-%m-%d')

    return render_template(
        'cierres.html',
        fechaInicio=fechaInicio,
        fechaFinal=fechaFinal,
        salon_id=salon_id,
        role=role
    )



### Usuarios ###
@app.route('/admin/users')
def list_users():
    if "user" not in session:
        return redirect(url_for("login", next=request.path))

    salon_id = session.get('salon_id')
    users = Usuario.query.filter_by(salon_id=salon_id).all()
    return render_template('users.html', users=users)
    

@app.route('/admin/users/add', methods=['POST'])
def add_user():
    if "user" not in session:
        return redirect(url_for("login", next=request.path))

    username = request.form['username'].strip()
    password = request.form['password']
    rol = request.form['rol']
    salon_id = session.get('salon_id')

    if not username or not password or not rol:
        flash("Faltan datos obligatorios.", "danger")
        return redirect(url_for('list_users'))

    # Validar si ya existe usuario con mismo nombre en este salón
    existente = Usuario.query.filter_by(username=username, salon_id=salon_id).first()
    if existente:
        flash("El nombre de usuario ya existe. Elija otro.", "danger")
        return redirect(url_for('list_users'))

    # Crear nuevo usuario
    hashed_pw = generate_password_hash(password)
    nuevo = Usuario(username=username, password=hashed_pw, rol=rol, salon_id=salon_id)

    db.session.add(nuevo)
    db.session.commit()

    flash("Usuario agregado correctamente.", "success")
    return redirect(url_for('list_users'))


@app.route('/admin/users/delete/<int:id>')
def delete_user(id):
    if "user" in session:
        user = Usuario.query.get_or_404(id)
        db.session.delete(user)
        db.session.commit()
        return redirect(url_for('list_users'))
    else:
        return redirect(url_for("login"))

@app.route('/admin/users/update/<int:id>', methods=['POST'])
def update_user_password(id):
    if "user" not in session:
        return redirect(url_for("login"))

    user = Usuario.query.get_or_404(id)
    new_password = request.form.get('new_password')

    if not new_password:
        return "La nueva contraseña es requerida", 400

    user.password = generate_password_hash(new_password)
    db.session.commit()

    return redirect(url_for('list_users'))





### Landing ### 

@app.route("/")
def public_landing():
    return render_template("public_landing.html")

@app.route("/app")
def app_landing():
    return render_template("index.html")

@app.route("/turnos")
def turnos():
    return redirect("https://www.fresha.com/es/a/barba-co-pineyro-avenida-presidente-bernardino-rivadavia-215-o1ukwtm0/all-offer?menu=true&pId=1429418")  # Si querés que redirija directo



### Metricas ### 


@app.route('/metricas')
def metricas():
    fecha_limite = datetime.now() - timedelta(days=30)

    servicios_mas_vendidos = obtener_servicios_mas_vendidos(fecha_limite)
    productos_mas_vendidos = obtener_productos_mas_vendidos(fecha_limite)
    horas_pico = obtener_horas_pico_por_media_hora(fecha_limite)
    membresias_vendidas = obtener_membresias_vendidas(fecha_limite)


    return render_template(
        "metricas.html",
        horas_pico=horas_pico,
        servicios_mas_vendidos=servicios_mas_vendidos,
        productos_mas_vendidos=productos_mas_vendidos,
        membresias_vendidas=membresias_vendidas,
    )


def obtener_servicios_mas_vendidos(fecha_limite):
    # Parte 1: servicios pagados
    resultados = (
        db.session.query(
            Servicio.name,
            Appointment.tipo_precio_servicio,
            func.count(Pago.id).label('cantidad_vendida')
        )
        .join(Appointment, Appointment.id == Pago.appointment_id)
        .join(Servicio, Servicio.id == Appointment.service_id)
        .filter(Pago.date >= fecha_limite)
        .group_by(Servicio.name, Appointment.tipo_precio_servicio)
        .all()
    )

    servicios = {}
    for nombre, tipo_precio, cantidad in resultados:
        if nombre not in servicios:
            servicios[nombre] = {
                "total": 0,
                "comun": 0,
                "amigo": 0,
                "descuento": 0,
                "membresia": 0  # este campo se llenará abajo
            }
        servicios[nombre][tipo_precio] += cantidad
        servicios[nombre]["total"] += cantidad

    # Parte 2: usos de membresías (no compradas, solo usadas)
    pagos = (
        db.session.query(Pago)
        .filter(Pago.date >= fecha_limite)
        .all()
    )

    for pago in pagos:
        if not pago.membresia_comprada and pago.appointment and pago.appointment.membresia:
            tipo = pago.appointment.membresia.tipo_membresia
            servicio = Servicio.query.get(tipo.servicio_id)
            if not servicio:
                continue

            nombre_servicio = servicio.name
            if nombre_servicio not in servicios:
                servicios[nombre_servicio] = {
                    "total": 0,
                    "comun": 0,
                    "amigo": 0,
                    "descuento": 0,
                    "membresia": 0
                }

            servicios[nombre_servicio]["membresia"] += 1
            servicios[nombre_servicio]["total"] += 1

    # Resultado final
    return [
        {
            "nombre": nombre,
            "total": datos["total"],
            "comun": datos["comun"],
            "amigo": datos["amigo"],
            "descuento": datos["descuento"],
            "membresia": datos["membresia"]
        }
        for nombre, datos in servicios.items()
    ]


def obtener_productos_mas_vendidos(fecha_limite):
    resultados = (
        db.session.query(
            Producto.name,
            func.sum(AppointmentTurno.cantidad).label('cantidad_total')
        )
        .join(AppointmentTurno.producto)  
        .join(Appointment, Appointment.id == AppointmentTurno.turno_id)
        .filter(Appointment.date >= fecha_limite)
        .group_by(Producto.name)
        .order_by(func.sum(AppointmentTurno.cantidad).desc())
        .all()
    )

    return [
        {"nombre": nombre, "cantidad": int(cantidad)}
        for nombre, cantidad in resultados
    ]


def obtener_horas_pico_por_media_hora(fecha_limite):
    media_hora_case = case(
        (extract('minute', Appointment.date) < 30, 0),
        else_=30
    )

    resultados = (
        db.session.query(
            extract('hour', Appointment.date).label('hora'),
            media_hora_case.label('media_hora'),
            func.count().label('cantidad')
        )
        .filter(Appointment.date >= fecha_limite)
        .group_by('hora', 'media_hora')
        .order_by(func.count().desc())
        .all()
    )

    return [
        (int(row.hora), int(row.media_hora), row.cantidad)
        for row in resultados
    ]


def obtener_membresias_vendidas(fecha_limite):
    resultados = (
        db.session.query(
            TipoMembresia.nombre,
            func.count(Pago.id).label('cantidad_vendida')
        )
        .join(Pago.membresia_comprada)
        .join(TipoMembresia, TipoMembresia.id == Membresia.tipo_membresia_id)
        .filter(Pago.date >= fecha_limite)
        .filter(Pago.membresia_comprada_id.isnot(None))
        .group_by(TipoMembresia.nombre)
        .order_by(func.count(Pago.id).desc())
        .all()
    )

    return [
        {"nombre": nombre, "cantidad": cantidad}
        for nombre, cantidad in resultados
    ]



### Agenda ###


@app.route('/availability/<int:barber_id>/day')
def get_barber_availability_day(barber_id):
    """
        Devuelve la disponibilidad de turnos de un barbero para una fecha específica.
        Parámetros:
            - fecha (YYYY-MM-DD) obligatorio
            - salon_id (opcional)
    """
    salon_id = request.args.get('salon_id', None)
    fecha_str = request.args.get('fecha', None)

    if not fecha_str:
        return jsonify({"error": "Parámetro 'fecha' obligatorio"}), 400

    try:
        fecha_obj = datetime.strptime(fecha_str, "%Y-%m-%d").date()
    except ValueError:
        return jsonify({"error": "Formato de fecha inválido, use YYYY-MM-DD"}), 400

    # Obtener todos los turnos del barbero en esa fecha
    query = TurnoCliente.query.filter(
        TurnoCliente.barber_id == barber_id,
        TurnoCliente.fecha == fecha_obj
    )
    if salon_id:
        query = query.filter(TurnoCliente.peluqueria_id == salon_id)

    turnos = query.all()

    # Definir horario de trabajo y intervalo de slots
    hora_inicio_jornada = time(11, 0)
    hora_fin_jornada = time(20, 0)
    intervalo_minutos = 30

    # Crear lista de slots del día
    slots = []
    current = datetime.combine(fecha_obj, hora_inicio_jornada)
    fin_jornada_dt = datetime.combine(fecha_obj, hora_fin_jornada)

    while current + timedelta(minutes=intervalo_minutos) <= fin_jornada_dt:
        slots.append(current.time())
        current += timedelta(minutes=intervalo_minutos)

    # Marcar slots ocupados
    horarios_ocupados = []
    for t in turnos:
        turno_inicio = datetime.combine(fecha_obj, t.hora_inicio)
        turno_fin = turno_inicio + timedelta(minutes=t.duracion_minutos)
        horarios_ocupados.append((turno_inicio.time(), turno_fin.time()))

    # Filtrar slots libres
    disponibilidad = []
    for slot in slots:
        slot_dt = datetime.combine(fecha_obj, slot)
        slot_fin = slot_dt + timedelta(minutes=intervalo_minutos)

        ocupado = False
        for inicio, fin in horarios_ocupados:
            if (slot >= inicio and slot < fin) or (slot_fin.time() > inicio and slot_fin.time() <= fin):
                ocupado = True
                break

        if not ocupado:
            disponibilidad.append(slot.strftime("%H:%M"))

    return jsonify({
        "barber_id": barber_id,
        "fecha": fecha_obj.strftime("%Y-%m-%d"),
        "disponibilidad": disponibilidad
    })



@app.route('/clientes/<int:client_dni>', methods=['GET'])
def get_cliente_by_dni(client_dni):
    """
    Devuelve un cliente a partir del DNI pasado en la URL.
    """
    # Buscar cliente por DNI
    cliente = Cliente.query.filter(Cliente.dni == str(client_dni)).first()

    if not cliente:
        return jsonify({"error": "Cliente no encontrado"}), 404

    return jsonify({
        "id": cliente.id,
        "nombre": cliente.nombre,
        "apellido": cliente.apellido,
        "email": cliente.email,
        "dni": cliente.dni,
        "telefono": cliente.telefono,
        "peluqueria_id": cliente.peluqueria_id,
        "created_at": cliente.created_at.isoformat()
    })


@app.route('/clientes', methods=['POST'])
@csrf.exempt
def crear_cliente():
    data = request.json

    # Validar campos obligatorios
    if not all(k in data for k in ("nombre", "apellido", "dni", "peluqueria_id")):
        return jsonify({"error": "Faltan campos obligatorios"}), 400

    # Verificar si el DNI ya existe para esa peluquería
    if Cliente.query.filter_by(dni=data['dni'], peluqueria_id=data['peluqueria_id']).first():
        return jsonify({"error": "El cliente con ese DNI ya existe en esta peluquería"}), 400

    # Crear cliente
    nuevo_cliente = Cliente(
        nombre=data['nombre'],
        apellido=data['apellido'],
        dni=data['dni'],
        email=data.get('email'),
        telefono=data.get('telefono'),
        peluqueria_id=data['peluqueria_id'],
        created_at=now_buenos_aires()
    )

    db.session.add(nuevo_cliente)
    db.session.commit()

    return jsonify({
        "id": nuevo_cliente.id,
        "nombre": nuevo_cliente.nombre,
        "apellido": nuevo_cliente.apellido,
        "dni": nuevo_cliente.dni,
        "email": nuevo_cliente.email,
        "telefono": nuevo_cliente.telefono,
        "peluqueria_id": nuevo_cliente.peluqueria_id,
        "created_at": nuevo_cliente.created_at.isoformat()
    }), 201
