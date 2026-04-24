from functools import wraps
from flask import session, redirect, url_for


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))

        from .models import Usuario
        usuario = Usuario.query.filter_by(username=session.get('user')).first()
        if not usuario or usuario.salon_id != session.get('salon_id'):
            session.clear()
            return redirect(url_for('login'))

        return f(*args, **kwargs)
    return decorated_function
