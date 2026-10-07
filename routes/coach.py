from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from models import db, User, Routine
import json

coach_bp = Blueprint('coach', __name__, url_prefix='/coach')

def coach_required(f):
    def decorated_function(*args, **kwargs):
        if session.get('role') not in ['coach', 'admin']:
            flash('Acceso permitido solo para entrenadores.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@coach_bp.route('/dashboard')
@coach_required
def dashboard():
    coach_id = session.get('user_id')
    coach = User.query.get(coach_id)
    
    alumnos = User.query.filter_by(role='student_custom').all()
    alumnos_data = []
    
    for a in alumnos:
        rutinas = Routine.query.filter_by(student_id=a.id).all()
        total = len(rutinas)
        completadas = sum(1 for r in rutinas if r.completado)
        porcentaje = int((completadas / total) * 100) if total > 0 else 0
        
        alumnos_data.append({
            'alumno': a,
            'total_rutinas': total,
            'completadas': completadas,
            'porcentaje': porcentaje
        })
        
    return render_template('coach/dashboard.html', alumnos_data=alumnos_data, coach=coach)

@coach_bp.route('/assign-routine/<int:student_id>', methods=['GET', 'POST'])
@coach_required
def assign_routine(student_id):
    student = User.query.get_or_404(student_id)
    coach_id = session.get('user_id')
    
    if request.method == 'POST':
        dia_semana = request.form.get('dia_semana')
        ejercicios_raw = request.form.get('ejercicios', '').strip().split('\n')
        comidas_raw = request.form.get('comidas', '').strip().split('\n')
        
        ejercicios = [e.strip() for e in ejercicios_raw if e.strip()]
        comidas = [c.strip() for c in comidas_raw if c.strip()]
        
        # Eliminar rutina previa de ese día si existía para sobreescribir
        Routine.query.filter_by(student_id=student.id, dia_semana=dia_semana).delete()
        
        nueva_rutina = Routine(
            student_id=student.id,
            coach_id=coach_id,
            dia_semana=dia_semana,
            ejercicios_json=json.dumps(ejercicios),
            comidas_json=json.dumps(comidas),
            completado=False
        )
        
        db.session.add(nueva_rutina)
        db.session.commit()
        flash(f'Rutina para {dia_semana} asignada correctamente a {student.nombre}.', 'success')
        return redirect(url_for('coach.assign_routine', student_id=student.id))
        
    rutinas = Routine.query.filter_by(student_id=student.id).all()
    for r in rutinas:
        r.ejercicios_list = json.loads(r.ejercicios_json) if r.ejercicios_json else []
        r.comidas_list = json.loads(r.comidas_json) if r.comidas_json else []
        
    return render_template('coach/assign_routine.html', student=student, rutinas=rutinas)

@coach_bp.route('/delete-routine/<int:routine_id>', methods=['POST'])
@coach_required
def delete_routine(routine_id):
    routine = Routine.query.get_or_404(routine_id)
    student_id = routine.student_id
    db.session.delete(routine)
    db.session.commit()
    flash('Rutina eliminada.', 'info')
    return redirect(url_for('coach.assign_routine', student_id=student_id))