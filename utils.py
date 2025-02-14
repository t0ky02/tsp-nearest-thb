from functools import wraps

from flask import  session, flash, redirect, url_for

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:  # Check if the user is logged in
            return redirect(url_for('login'))
        return f(*args, **kwargs)
        
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('role') != 'admin':
            flash('Anda tidak punya akses ke halaman ini.', 'danger')
            return redirect(url_for('index'))  # Redirect jika bukan admin
        return f(*args, **kwargs)
    return decorated_function

def driver_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('role') != 'driver':
            flash('Anda tidak punya akses ke halaman ini.', 'danger')
            return redirect(url_for('index'))  # Redirect jika bukan driver
        return f(*args, **kwargs)
    return decorated_function
