from flask import Blueprint, render_template, redirect, url_for, flash, session, jsonify, request
from models import db, User, Routine
import json

student_bp = Blueprint('student', __name__, url_prefix='/student')

@student_bp.route('/portal')
def portal():
    if session.get('role') != 'student_custom':
        flash('Debes iniciar sesión como alumno personalizado.', 'warning')
        return redirect(url_for('auth.login'))
        
    student = User.query.get_or_404(session.get('user_id'))
    
    # Obtener todas las rutinas asignadas
    rutinas = Routine.query.filter_by(student_id=student.id).all()
    
    # Decodificar JSONs para enviar a Jinja
    for r in rutinas:
        r.ejercicios_list = json.loads(r.ejercicios_json) if r.ejercicios_json else []
        r.comidas_list = json.loads(r.comidas_json) if r.comidas_json else []
        
    return render_template('student/dashboard.html', student=student, rutinas=rutinas)

@student_bp.route('/complete-workout/<int:routine_id>', methods=['POST'])
def complete_workout(routine_id):
    routine = Routine.query.get_or_404(routine_id)
    routine.completado = True
    db.session.commit()
    return jsonify({'success': True, 'message': '¡Entrenamiento registrado con éxito! 🎉'})