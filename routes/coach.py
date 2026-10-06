from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import db, User, Routine
import json

coach_bp = Blueprint('coach', __name__, url_prefix='/coach')

def coach_required(f):
    def decorated_function(*args, **kwargs):
        if session.get('role') not in ['coach', 'admin']:
            flash('Acceso denegado. Permiso exclusivo de Entrenador o Administrador.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@coach_bp.route('/dashboard')
@coach_required
def dashboard():
    alumnos = User.query.filter_by(is_custom_student=True).all()
    coach = User.query.get(session.get('user_id'))
    return render_template('coach/dashboard.html', alumnos=alumnos, coach=coach)

@coach_bp.route('/assign-routine/<int:student_id>', methods=['GET', 'POST'])
@coach_required
def assign_routine(student_id):
    student = User.query.get_or_404(student_id)
    
    if request.method == 'POST':
        dia = request.form.get('dia_semana')
        ejercicios_raw = request.form.get('ejercicios') # Separados por comas o saltos de línea
        comidas_raw = request.form.get('comidas')
        
        # Formatear como arreglos JSON
        ejercicios_list = [e.strip() for e in ejercicios_raw.split('\n') if e.strip()]
        comidas_list = [c.strip() for c in comidas_raw.split('\n') if c.strip()]
        
        # Eliminar rutina anterior de ese día si existe
        Routine.query.filter_by(student_id=student.id, dia_semana=dia).delete()
        
        nueva_rutina = Routine(
            student_id=student.id,
            coach_id=session.get('user_id'),
            dia_semana=dia,
            ejercicios_json=json.dumps(ejercicios_list),
            comidas_json=json.dumps(comidas_list),
            completado=False
        )
        
        db.session.add(nueva_rutina)
        db.session.commit()
        flash(f'Rutina de {dia} asignada a {student.nombre}.', 'success')
        return redirect(url_for('coach.dashboard'))
        
    return render_template('coach/assign_routine.html', student=student)