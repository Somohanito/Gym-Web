from flask import Blueprint, render_template, redirect, url_for, session, flash, jsonify
from models import db, User, Routine
from datetime import datetime
import json

student_bp = Blueprint('student', __name__, url_prefix='/student')

def student_required(f):
    def decorated_function(*args, **kwargs):
        if session.get('role') not in ['student_custom', 'admin']:
            flash('Acceso permitido solo para alumnos personalizados.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@student_bp.route('/portal')
@student_bp.route('/dashboard')
@student_required
def portal():
    student_id = session.get('user_id')
    student = User.query.get(student_id)
    rutinas = Routine.query.filter_by(student_id=student.id).all()
    hoy = datetime.now().date()
    
    for r in rutinas:
        r.ejercicios_list = json.loads(r.ejercicios_json) if r.ejercicios_json else []
        r.comidas_list = json.loads(r.comidas_json) if r.comidas_json else []
        
    return render_template('student/dashboard.html', student=student, rutinas=rutinas, hoy=hoy)

@student_bp.route('/dashboard-alias')
@student_required
def dashboard():
    return portal()

# --- NUEVA RUTA: Recibe el clic del botón y guarda el progreso ---
@student_bp.route('/complete-workout/<int:routine_id>', methods=['POST'])
@student_required
def complete_workout(routine_id):
    routine = Routine.query.get_or_404(routine_id)
    student_id = session.get('user_id')
    
    # Seguridad: Evita que alguien complete la rutina de otro alumno
    if routine.student_id != student_id:
        return jsonify({'success': False, 'message': 'Acceso denegado.'}), 403
        
    student = User.query.get(student_id)
    
    # 1. Marcar la rutina como completada
    routine.completado = True
    routine.fecha_completado = datetime.now()
    
    # 2. Sumar puntos a las estadísticas del alumno
    student.dias_entrenados_semana = (student.dias_entrenados_semana or 0) + 1
    student.racha_dias = (student.racha_dias or 0) + 1
    student.ultima_racha_fecha = datetime.now().date()
    
    # 3. Guardar en la base de datos
    db.session.commit()
    
    # 4. Responder al JavaScript para que lance los confetis y el modal
    return jsonify({
        'success': True, 
        'message': '¡Excelente trabajo! Cada día estás más cerca de tu meta. 💪',
        'racha': student.racha_dias
    })