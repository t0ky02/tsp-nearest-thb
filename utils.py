from functools import wraps

from flask import make_response, request, session, flash, redirect, url_for

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:  # Check if the user is logged in
            flash('You need to log in to access this page.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
        
        
    return decorated
