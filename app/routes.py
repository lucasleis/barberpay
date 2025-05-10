from flask import render_template, request, redirect, url_for
from . import db
from .models import Barber, Service, Appointment, Payment, PaymentMethodEnum
from flask import current_app as app

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/barbers')
def list_barbers():
    barbers = Barber.query.filter_by(active=True).all()
    return render_template('barbers.html', barbers=barbers)

@app.route('/barbers/add', methods=['POST'])
def add_barber():
    name = request.form['name']
    db.session.add(Barber(name=name))
    db.session.commit()
    return redirect(url_for('list_barbers'))

@app.route('/barbers/delete/<int:id>')
def delete_barber(id):
    barber = Barber.query.get(id)
    barber.active = False
    db.session.commit()
    return redirect(url_for('list_barbers'))

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

@app.route('/services')
def list_services():
    services = Service.query.all()
    return render_template('services.html', services=services)

@app.route('/services/add', methods=['POST'])
def add_service():
    name = request.form['name']
    price = float(request.form['price'])
    db.session.add(Service(name=name, price=price))
    db.session.commit()
    return redirect(url_for('list_services'))

