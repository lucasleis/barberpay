from flask import current_app as app, render_template, request, redirect, url_for, session, flash
from . import db
from .models import Peluqueria, Empleado, Servicio, MetodoPago, Pago, Appointment, Producto, Membresia
from .auth import login_required
from sqlalchemy.orm import aliased
from datetime import datetime, timedelta, time
from collections import defaultdict
# from backports.zoneinfo import ZoneInfo
from zoneinfo import ZoneInfo


# Funciones auxiliares
"""
def get_payment_page_data(salon_id):
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
        .add_entity(MetodoPago1)
        .add_entity(MetodoPago2)
        .order_by(Pago.date.desc())
        .limit(10)
        .all()
    )

    pagos_data = []
    for pago, method1, method2 in pagos_query:
        pago.method1 = method1
        pago.method2 = method2
        pagos_data.append(pago)

    barbers = Empleado.query.filter_by(active=True, peluqueria_id=salon_id).all()
    services = Servicio.query.filter_by(peluqueria_id=salon_id).all()
    methods = MetodoPago.query.filter_by(active=True, peluqueria_id=salon_id).all()

    return pagos_data, barbers, services, methods
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
        .join(Appointment.service)
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
    
@app.route('/admin/products/update_quantity/<int:id>', methods=['POST'])
def update_product_quantity(id):
    if "user" in session:
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
    else:
        return redirect(url_for("login"))

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


### Membresias ###
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

    if request.method == 'POST':
        try:
            barber_id = request.form.get('barber_id')
            if not (barber_id ):
                raise ValueError("Faltan datos del peluquero o servicio.")
            
            tip = float(request.form.get('tip') or 0.0)
            service_id = request.form.get('service_id')
            product_id = request.form.get('product_id')
            method1 = int(request.form.get('method1'))
            amount1 = float(request.form.get('amount1') or 0)

            toggle_servicio = 'toggleServicio' in request.form
            toggle_producto = 'toggleProducto' in request.form
            
            if toggle_producto:
                # print("Toggle de Producto activado")
                appointment = Appointment(
                    barber_id=barber_id,
                    productos_id=product_id,
                    peluqueria_id=salon_id
                )

            if toggle_servicio:
                # print("Toggle de Servicio activado")
                appointment = Appointment(
                    barber_id=barber_id,
                    service_id=service_id,
                    peluqueria_id=salon_id
                )

            db.session.add(appointment)
            db.session.commit()

            if request.form.get('amount2'):
                amount2 = float(request.form.get('amount2') or 0)
                method2 = int(request.form.get('method2'))
            else:
                amount2 = 0
                method2 = None

            # print("datetime.now:", datetime.now(ZoneInfo("America/Argentina/Buenos_Aires")))

            pago = Pago(
                appointment_id=appointment.id,
                payment_method1_id=method1,
                payment_method2_id=method2,
                amount_method1=amount1,
                amount_method2=amount2,
                amount_tip=tip,
                peluqueria_id=salon_id,
                #date= now_buenos_aires()
                date=datetime.now(ZoneInfo("America/Argentina/Buenos_Aires"))
            )
            db.session.add(pago)
            db.session.commit()
            flash("Pago registrado con éxito.", "success")
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
        products=products 
    )

@app.route('/payments/delete/<int:pago_id>', methods=['POST'])
def delete_payment(pago_id):
    session['salon_id'] = 1
    salon_id = session.get("salon_id")

    pago = Pago.query.get_or_404(pago_id)

    try:
        appointment = Appointment.query.get(pago.appointment_id)
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
"""
@app.route('/cierre/semanal')
def show_cierre_semanal():
    return render_template('cierre_semanal.html')
"""

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

