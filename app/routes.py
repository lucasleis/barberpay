from flask import current_app as app, render_template, request, redirect, url_for, session, flash
from . import db
from .models import Empleado, Servicio, MetodoPago, Pago, Appointment, Producto, Membresia, TipoMembresia, AppointmentTurno
from .auth import login_required
from sqlalchemy.orm import aliased, selectinload, joinedload
from datetime import datetime, timedelta, time
from collections import defaultdict
# from backports.zoneinfo import ZoneInfo
from zoneinfo import ZoneInfo


# Funciones auxiliares
"""
def get_payment_page_data(salon_id):
    MetodoPago1 = aliased(MetodoPago)
    MetodoPago2 = aliased(MetodoPago)

    # Obtener fecha actual (desde las 00:00 hasta las 23:59:59 del día de hoy)
    hoy = datetime.today().date()
    inicio_dia = datetime.combine(hoy, time.min)  # 00:00:00
    fin_dia = datetime.combine(hoy, time.max)     # 23:59:59.999999

    pagos_query = (
        Pago.query
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
"""
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

def get_cierre_semanal_data(salon_id):
    MetodoPago1 = aliased(MetodoPago)
    MetodoPago2 = aliased(MetodoPago)

    pagos_query = (
        Pago.query
        .join(Pago.appointment)
        .join(Appointment.barber)
        .join(Appointment.service)
        .join(MetodoPago1, Pago.payment_method1_id == MetodoPago1.id)
        .outerjoin(MetodoPago2, Pago.payment_method2_id == MetodoPago2.id)
        .filter(Pago.peluqueria_id == salon_id)
        .order_by(Pago.date.desc())
        .add_entity(MetodoPago1)
        .add_entity(MetodoPago2)
        .all()
    )

    pagos_por_semana = defaultdict(list)

    for pago, method1, method2 in pagos_query:
        appointment = pago.appointment
        barber = appointment.barber
        service = appointment.service

        valor_servicio = float(service.precio)
        porcentaje_empleado = barber.porcentaje
        pago_empleado = valor_servicio * (porcentaje_empleado / 100)
        propina = float(pago.amount_tip or 0)
        pago_empleado_con_propina = pago_empleado + propina
        pago_propietario = valor_servicio - pago_empleado

        fecha_pago = pago.date.date()
        cierre_semana = fecha_pago + timedelta(days=(6 - fecha_pago.weekday()))

        pagos_por_semana[cierre_semana].append({
            "fecha": fecha_pago,
            "empleado": barber.name,
            "servicio": service.name,
            "valor_servicio": valor_servicio,
            "porcentaje_empleado": porcentaje_empleado,
            "pago_empleado": pago_empleado_con_propina,
            "pago_propietario": pago_propietario,
            "metodo_pago1": method1.nombre if method1 else None,
            "monto1": float(pago.amount_method1),
            "metodo_pago2": method2.nombre if method2 else None,
            "monto2": float(pago.amount_method2 or 0),
            "propina": propina,
        })

    cierre_ordenado = []

    for fecha_cierre, pagos in sorted(pagos_por_semana.items(), reverse=True):
        total_general = 0
        total_propietario = 0
        total_empleados = defaultdict(lambda: {"monto": 0, "cortes": 0})
        total_metodos_pago = defaultdict(float)

        for p in pagos:
            total_general += p["valor_servicio"] + p["propina"]
            total_propietario += p["pago_propietario"]

            total_empleados[p["empleado"]]["monto"] += p["pago_empleado"]
            total_empleados[p["empleado"]]["cortes"] += 1

            if p["metodo_pago1"]:
                total_metodos_pago[p["metodo_pago1"]] += p["monto1"]
            if p["metodo_pago2"]:
                total_metodos_pago[p["metodo_pago2"]] += p["monto2"]

        fecha_inicio = fecha_cierre - timedelta(days=6)
        
        cierre_ordenado.append({
            "fecha_inicio": fecha_inicio,
            "fecha_cierre": fecha_cierre,
            "pagos": pagos,
            "totales": {
                "monto_total": total_general,
                "propietario_total": total_propietario,
                "empleados": dict(total_empleados),
                "metodos_pago": dict(total_metodos_pago),
            }
        })

    return cierre_ordenado

def get_cierre_entre_fechas_data(salon_id, fecha_inicio_str, fecha_final_str):
    MetodoPago1 = aliased(MetodoPago)
    MetodoPago2 = aliased(MetodoPago)

    # Convertir strings a objetos datetime.date
    fecha_inicio = datetime.combine(datetime.strptime(fecha_inicio_str, "%Y-%m-%d"), time.min)  # 00:00:00
    fecha_final = datetime.combine(datetime.strptime(fecha_final_str, "%Y-%m-%d"), time.max)    # 23:59:59.999999

    pagos_query = (
        Pago.query
        .join(Pago.appointment)
        .join(Appointment.barber)
        .join(Appointment.service)
        .join(MetodoPago1, Pago.payment_method1_id == MetodoPago1.id)
        .outerjoin(MetodoPago2, Pago.payment_method2_id == MetodoPago2.id)
        .filter(
            Pago.peluqueria_id == salon_id,
            Pago.date >= fecha_inicio,
            Pago.date <= fecha_final
        )
        .order_by(Pago.date.desc())
        .add_entity(MetodoPago1)
        .add_entity(MetodoPago2)
        .all()
    )

    pagos_por_semana = defaultdict(list)

    for pago, method1, method2 in pagos_query:
        appointment = pago.appointment
        barber = appointment.barber
        service = appointment.service

        valor_servicio = float(service.precio)
        porcentaje_empleado = barber.porcentaje
        pago_empleado = valor_servicio * (porcentaje_empleado / 100)
        propina = float(pago.amount_tip or 0)
        pago_empleado_con_propina = pago_empleado + propina
        pago_propietario = valor_servicio - pago_empleado

        fecha_pago = pago.date.date()
        cierre_semana = fecha_pago + timedelta(days=(6 - fecha_pago.weekday()))

        pagos_por_semana[cierre_semana].append({
            "fecha": fecha_pago,
            "empleado": barber.name,
            "servicio": service.name,
            "valor_servicio": valor_servicio,
            "porcentaje_empleado": porcentaje_empleado,
            "pago_empleado": pago_empleado_con_propina,
            "pago_propietario": pago_propietario,
            "metodo_pago1": method1.nombre if method1 else None,
            "monto1": float(pago.amount_method1),
            "metodo_pago2": method2.nombre if method2 else None,
            "monto2": float(pago.amount_method2 or 0),
            "propina": propina,
        })

    cierre_ordenado = []

    for fecha_cierre, pagos in sorted(pagos_por_semana.items(), reverse=True):
        total_general = 0
        total_propietario = 0
        total_empleados = defaultdict(lambda: {"monto": 0, "cortes": 0})
        total_metodos_pago = defaultdict(float)

        for p in pagos:
            total_general += p["valor_servicio"] + p["propina"]
            total_propietario += p["pago_propietario"]

            total_empleados[p["empleado"]]["monto"] += p["pago_empleado"]
            total_empleados[p["empleado"]]["cortes"] += 1

            if p["metodo_pago1"]:
                total_metodos_pago[p["metodo_pago1"]] += p["monto1"]
            if p["metodo_pago2"]:
                total_metodos_pago[p["metodo_pago2"]] += p["monto2"]

        cierre_ordenado.append({
            "fecha_inicio": fecha_inicio,
            "fecha_cierre": fecha_final,
            "pagos": pagos,
            "totales": {
                "monto_total": total_general,
                "propietario_total": total_propietario,
                "empleados": dict(total_empleados),
                "metodos_pago": dict(total_metodos_pago),
            }
        })

    return cierre_ordenado

def calcular_total_servicio(service_id):
    """Calcula el total para un servicio"""
    if not service_id:
        return 0.0
    service = Servicio.query.get(service_id)
    return service.precio if service else 0.0

def calcular_total_producto(product_id, cantidad):
    """Calcula el total para un producto"""
    if not product_id or not cantidad:
        return 0.0
    product = Producto.query.get(product_id)
    return (product.precio * cantidad) if product else 0.0

def calcular_total_pagado(request_form, toggle_servicio, toggle_producto, product_precio=0, product_cantidad=0):
    """Calcula el total pagado según el método de pago y los toggles"""
    tip = float(request_form.get('tip') or 0.0)
    multipagos = 'togglemultiPayment' in request_form
    
    if multipagos:
        amount1 = float(request_form.get('amount_method_multi_1') or 0)
        amount2 = float(request_form.get('amount_method_multi_2') or 0)
        return amount1 + amount2 + tip
    
    amount_simple = float(request_form.get('amount_simple') or 0)
    
    if toggle_servicio and toggle_producto:
        return amount_simple + (product_precio * product_cantidad) + tip
    elif toggle_servicio:
        return amount_simple + tip
    elif toggle_producto:
        return (product_precio * product_cantidad) + tip
    
    return 0.0

def calcular_total_real(toggle_servicio, toggle_producto, service_id=None, product_id=None, product_cantidad=0):
    """Calcula el total real sumando servicio y/o producto"""
    total = 0.0
    
    if toggle_servicio:
        total += calcular_total_servicio(service_id)
    
    if toggle_producto:
        total += calcular_total_producto(product_id, product_cantidad)
    
    return total


@app.route('/')
def index():
    return render_template('index.html')

### Administrador ###

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

@app.route("/logout")
def logout():
    session.pop("user", None)
    session.pop("salon_id", None)
    return redirect(url_for("login"))

@app.route('/dashboard')
def dashboard():
    if "user" in session:
        return render_template('dashboard.html')
    else:
        return redirect(url_for("login"))


### Empleados ###

@app.route('/admin/barbers')
def list_barbers():
    if "user" in session:
        salon_id = session.get('salon_id')
        barbers = Empleado.query.filter_by(active=True, peluqueria_id=salon_id).all()
        return render_template('barbers.html', barbers=barbers)
    else:
        return redirect(url_for("login"))

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


### Servicios ###

@app.route('/admin/services')
def list_services():
    if "user" in session:
        salon_id = session.get('salon_id')
        services = Servicio.query.filter_by(active=True, peluqueria_id=salon_id).all()
        return render_template('services.html', services=services)
    else:
        return redirect(url_for("login"))

@app.route('/admin/services/add', methods=['POST'])
def add_service():
    if "user" in session:
        name = request.form.get('name')
        precio = float(request.form.get('precio', 0))

        try:
            precio_amigo = float(request.form.get('precio_amigo', 0) or 0)
        except ValueError:
            precio_amigo = 0

        try:
            precio_descuento = float(request.form.get('precio_descuento', 0) or 0)
        except ValueError:
            precio_descuento = 0

        salon_id = session.get('salon_id')

        db.session.add(Servicio(
            name=name,
            precio=precio,
            precio_amigo=precio_amigo,
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
    if "user" in session:
        name = request.form['name']
        precio = float(request.form['precio'])
        salon_id = session.get('salon_id')
        cantidad = int(request.form['cantidad'])
        db.session.add(Producto(name=name, precio=precio, peluqueria_id=salon_id,cantidad=cantidad))
        db.session.commit()
        return redirect(url_for('list_products'))
    else:
        return redirect(url_for("login"))
    
@app.route('/products/update_quantity/<int:id>', methods=['POST'])
def update_product_quantity(id):
    cantidad_extra = int(request.form['cantidad'])  # Cantidad a sumar
    salon_id = session.get('salon_id')

    # Buscar el producto por ID y peluquería
    product = Producto.query.filter_by(id=id, peluqueria_id=salon_id).first()

    if product:
        product.cantidad = cantidad_extra
        db.session.commit()
        return redirect(url_for('list_products'))
    else:
        return "Producto no encontrado o no pertenece al salón", 404

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


### Tipos de Membresias ###

@app.route('/admin/memberships')
def list_memberships():
    if "user" in session:
        salon_id = session.get('salon_id')
        tipos = TipoMembresia.query.filter_by(peluqueria_id=salon_id).all()
        return render_template('memberships.html', tipos_membresia=tipos)
    else:
        return redirect(url_for("login"))

@app.route('/admin/memberships/add', methods=['POST'])
def add_membership():
    if "user" in session:
        salon_id = session.get('salon_id')
        nombre = request.form['nombre']
        precio = request.form['precio']
        usos = request.form['cantidad'] 

        nueva = TipoMembresia(
            peluqueria_id=salon_id,
            nombre=nombre,
            precio=precio,
            usos=usos
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

"""
    @app.route('/membresia/descontar/<int:id>', methods=['POST'])
    def descontar_membresia(id):
        salon_id = session.get('salon_id')

        # Buscar la membresía por ID y peluquería
        membresia = Membresia.query.filter_by(id=id, peluqueria_id=salon_id).first()

        if membresia:
            if membresia.cantidad > 0:
                membresia.cantidad -= 1
                db.session.commit()
                return redirect(url_for('some_view_name'))  # Cambiá esto según a dónde querés redirigir
            else:
                return "La membresía ya no tiene usos disponibles.", 400
        else:
            return "Membresía no encontrada o no pertenece al salón", 404
"""


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


### Pagos ###

@app.route('/payments/new', methods=['GET', 'POST'])
def add_payment():
    session['salon_id'] = 1
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
                service_id = request.form.get('service_id')
                if not service_id:
                    raise ValueError("Debe seleccionarse un servicio.")
                appointment.service_id = service_id

                if request.form.get('precioDescuentoCheckbox') == 'on':
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

                check_membresia = request.form.get('membresiaCheckbox') 
                if check_membresia == 'on':
                    num_membresia = request.form.get('check_membresia') 
                    membresia = Membresia.query.get(num_membresia)
                    if not membresia:
                        raise ValueError("Membresía no encontrada.")

                    if membresia.usos_disponibles <= 0:
                        raise ValueError("No hay usos disponibles para descontar en esta membresía.")

                    membresia.usos_disponibles -= 1
                    db.session.add(membresia)
                    appointment.membresia_id = membresia.id
                    flash(f"Membresía #{membresia.id}: Quedan {membresia.usos_disponibles} usos disponibles.", "success")
                else:
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
                    appointment.membresia_id = membresia_real.id

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
                # service = Servicio.query.get(service_id)
                # total_real += service.precio if service else 0  
                precio = request.form.get('servicePrice')
                precio = precio.split("$")
                service_price = int(precio[1] or 0)
                total_real += service_price

            if toggle_producto:
                total_real += total_producto

            if toggle_membresia:   
                membresia = TipoMembresia.query.get(membresia_id)
                total_real += float(membresia.precio) if membresia else 0

                if check_membresia == 'on':
                    total_real = 0 

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
                flash(f"El total abonado (${total_pagado}) no coincide con el total real (${total_real}).", "danger")
                #raise ValueError(f"El total abonado (${total_pagado}) no coincide con el total real (${total_real}).")


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
            )

            db.session.add(pago)
            db.session.commit()
            flash("Pago registrado con éxito.", "success")

            if membresia_real:
                flash(f"Numero de membresia: {membresia_real.id}", "success")

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
    session['salon_id'] = 1
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
@app.route("/cierre_semanal")
def cierre_semanal():
    session['salon_id'] = 1
    raw_salon_id = request.form.get("salon_id") or session.get("salon_id")

    try:
        salon_id = int(str(raw_salon_id).strip("{} "))
    except (ValueError, TypeError):
        flash("ID de peluquería inválido.", "danger")
        return redirect(url_for("index"))

    semanas_cierre = get_cierre_semanal_data(salon_id)
    return render_template("cierre_semanal.html", semanas=semanas_cierre)

@app.route("/cierres")
def cierre_entre_dias():
    session['salon_id'] = 1
    raw_salon_id = request.form.get("salon_id") or session.get("salon_id")

    try:
        salon_id = int(str(raw_salon_id).strip("{} "))
    except (ValueError, TypeError):
        flash("ID de peluquería inválido.", "danger")
        return redirect(url_for("index"))

    fecha_inicio = request.args.get("fechaInicio")
    fecha_final = request.args.get("fechaFinal")

    if fecha_inicio and fecha_final:
        semanas = get_cierre_entre_fechas_data(salon_id, fecha_inicio, fecha_final)
    else:
        semanas = get_cierre_semanal_data(salon_id)

    return render_template("cierre_entre_dias.html", semanas=semanas)  

