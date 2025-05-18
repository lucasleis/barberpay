from flask import current_app as app, render_template, request, redirect, url_for, session, flash
from . import db
from .models import Barber, Service, Appointment, Payment, PaymentMethodEnum
from .auth import login_required


@app.route('/')
def index():
    return render_template('index.html')

### Adminstrador ###

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if (username == app.config['ADMIN_USERNAME'] and
            password == app.config['ADMIN_PASSWORD']):
            session.permanent = True
            session['user'] = username 
            return redirect(url_for('dashboard'))
        else:
            flash("Usuario o contraseña incorrectos.")
            return redirect(url_for("login"))

    # Si ya está logueado, redirigir directamente
    if "user" in session:
        return redirect(url_for("dashboard"))
    
    return render_template('login.html')

@app.route("/logout")
def logout():
    session.pop("user", None)
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
        # return f"Bienvenido {session['user']}!"
        barbers = Barber.query.filter_by(active=True).all()
        return render_template('barbers.html', barbers=barbers)
    else:
        return redirect(url_for("login"))
    
@app.route('/admin/barbers/add', methods=['POST'])
def add_barber():
    if "user" in session:
        name = request.form['name']
        db.session.add(Barber(name=name))
        db.session.commit()
        return redirect(url_for('list_barbers'))
    else:
        return redirect(url_for("login"))

@app.route('/admin/barbers/delete/<int:id>')
def delete_barber(id):
    if "user" in session:
        barber = Barber.query.get(id)
        barber.active = False
        db.session.commit()
        return redirect(url_for('list_barbers'))
    else:
        return redirect(url_for("login"))

@app.route('/admin/services')
def list_services():
    if "user" in session:
        services = Service.query.all()
        return render_template('services.html', services=services)
    else:
        return redirect(url_for("login"))

@app.route('/admin/services/add', methods=['POST'])
def add_service():
    if "user" in session:
        name = request.form['name']
        price = float(request.form['price'])
        db.session.add(Service(name=name, price=price))
        db.session.commit()
        return redirect(url_for('list_services'))
    else:
        return redirect(url_for("login"))

@app.route('/admin/services/delete/<int:id>')
def delete_service(id):
    if "user" in session:
        service = Service.query.get(id)
        db.session.delete(service)
        db.session.commit()
        return redirect(url_for('list_services'))
    else:
        return redirect(url_for("login"))


### Peluqueros ###

@app.route('/payments/new', methods=['GET', 'POST'])
def add_payment():
    if request.method == 'POST':
        barber_id = request.form['barber_id']
        service_id = request.form['service_id']
        methods = request.form.getlist('method')
        amounts = request.form.getlist('amount')

        appointment = Appointment(barber_id=barber_id, service_id=service_id)
        db.session.add(appointment)
        db.session.commit()

        for method, amount in zip(methods, amounts):
            db.session.add(Payment(
                appointment_id=appointment.id,
                method=PaymentMethodEnum[method],
                amount=float(amount)
            ))
        db.session.commit()

        return redirect(url_for('index'))

    barbers = Barber.query.filter_by(active=True).all()
    services = Service.query.all()
    return render_template('add_payment.html', barbers=barbers, services=services, methods=PaymentMethodEnum)
