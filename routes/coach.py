from flask import Blueprint, render_template, redirect, url_for, flash, session
from models import db, User

coach_bp = Blueprint('coach', __name__, url_prefix='/coach')

def coach_required(f):
    def decorated_function(*args, **kwargs):
        if session.get('role') not in ['coach', 'admin']:
            flash('Acceso denegado.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@coach_bp.route('/dashboard')
@coach_required
def dashboard():
    # Obtener alumnos asignados o personalizados
    alumnos = User.query.filter_by(is_custom_student=True).all()
    coach = User.query.get(session.get('user_id'))
    
    return render_template('coach/dashboard.html', alumnos=alumnos, coach=coach)