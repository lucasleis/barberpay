from flask import current_app as app, render_template, request, redirect, url_for, session, flash
from . import db
from .models import Peluqueria, Empleado, Servicio, MetodoPago, Pago, Appointment
from .auth import login_required

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
        salon_id = session.get('salon_id')
        db.session.add(Empleado(name=name, peluqueria_id=salon_id))
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

@app.route('/admin/services')
def list_services():
    if "user" in session:
        salon_id = session.get('salon_id')
        services = Servicio.query.filter_by(peluqueria_id=salon_id).all()
        return render_template('services.html', services=services)
    else:
        return redirect(url_for("login"))

@app.route('/admin/services/add', methods=['POST'])
def add_service():
    if "user" in session:
        name = request.form['name']
        precio = float(request.form['precio'])
        salon_id = session.get('salon_id')
        db.session.add(Servicio(name=name, precio=precio, peluqueria_id=salon_id))
        db.session.commit()
        return redirect(url_for('list_services'))
    else:
        return redirect(url_for("login"))

@app.route('/admin/services/delete/<int:id>')
def delete_service(id):
    if "user" in session:
        service = Servicio.query.get(id)
        db.session.delete(service)
        db.session.commit()
        return redirect(url_for('list_services'))
    else:
        return redirect(url_for("login"))

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
        print(request.form) 
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
        db.session.delete(method)
        db.session.commit()
        return redirect(url_for('list_payment_methods'))
    else:
        return redirect(url_for("login"))


### Peluqueros ###
@app.route('/payments/new', methods=['GET', 'POST'])
def add_payment():
    print("Form data:", request.form)
    print("Args data:", request.args)

    session['salon_id'] = 1 

    raw_salon_id = request.form.get("salon_id") or session.get("salon_id")

    if raw_salon_id:
        try:
            salon_id = int(str(raw_salon_id).strip("{} ").strip())
        except ValueError:
            flash("ID de peluquería inválido.", "danger")
            return redirect(url_for("index"))
    else:
        flash("No se puede determinar la peluquería.", "danger")
        return redirect(url_for("index"))

    if not salon_id:
        flash("No se puede determinar la peluquería.", "danger")
        return redirect(url_for("index"))

    print(f"salon_id: {salon_id}")
    peluqueria_id=int(salon_id)

    barbers = Empleado.query.filter_by(active=True, peluqueria_id=peluqueria_id).all()
    services = Servicio.query.filter_by(peluqueria_id=peluqueria_id).all()
    methods = MetodoPago.query.filter_by(active=True, peluqueria_id=peluqueria_id).all()

    print(f"")
    if request.method == 'POST':
        barber_id = request.form.get('barber_id')
        # print(f"barber_id: {barber_id}")
        
        service_id = request.form.get('service_id')
        # print(f"service_id: {service_id}")

        tip = float(request.form.get('tip') or 0.0)
        # print(f"tip: {tip}")
        
        method1 = int(request.form.get('method1'))
        # print(f"method1: {method1}")
        
        # amount1 = float(request.form.get('amount1'))
        amount1 = request.form.get('amount1')
        # print(f"amount1: {amount1}")

        if not (barber_id and service_id):
            flash("Faltan datos del peluquero o servicio.", "danger")
            return render_template(
                'add_payment.html',
                barbers=barbers,
                services=services,
                methods=methods
            )

        try:
            # Crear la cita
            appointment = Appointment(
                barber_id=barber_id,
                service_id=service_id,
                peluqueria_id=peluqueria_id
            )
            db.session.add(appointment)
            db.session.commit()

            # Pago múltiple
            if request.form.get('amount1') and request.form.get('amount2'):
                print("Entrando al bloque de múltiples métodos de pago")

                amount2 = float(request.form.get('amount2') or 0)
                method2 = int(request.form.get('method2'))
                # print(f"amount1: {amount1}, amount2: {amount2}")
                # print(f"method1: {method1}, method2: {method2}")

                pago = Pago(
                    appointment_id=appointment.id,
                    payment_method1_id=method1,
                    payment_method2_id=method2,
                    amount_method1=amount1,
                    amount_method2=amount2,
                    amount_tip=tip,
                    peluqueria_id=peluqueria_id
                )
            else:
                # Pago simple
                pago = Pago(
                    appointment_id=appointment.id,
                    payment_method1_id=method1,
                    payment_method2_id=None,
                    amount_method1=amount1,
                    amount_method2=0,
                    amount_tip=tip,
                    peluqueria_id=peluqueria_id
                )
            #print(f"Pago creado")
            db.session.add(pago)
            print(f"Pago added")

            db.session.commit()
            flash("Pago registrado con éxito.", "success")
            return redirect(url_for('index'))

        except Exception as e:
            print(f"Exception ocurred: {e}")
            db.session.rollback()
            flash(f"Error al registrar el pago: {str(e)}", "danger")
            return render_template(
                'add_payment.html',
                barbers=barbers,
                services=services,
                methods=methods
            )

    return render_template(
        'add_payment.html',
        barbers=barbers,
        services=services,
        methods=methods
    )
