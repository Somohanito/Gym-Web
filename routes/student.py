from flask import Blueprint, render_template, redirect, url_for, flash, session, jsonify, request
from models import db, User, Routine, Attendance
from datetime import datetime, timedelta
import json
import random

student_bp = Blueprint('student', __name__, url_prefix='/student')

FRASES_DIARIAS = [
    "🔥 ¡Brutal entrenamiento! Un paso más cerca de tu versión imparable.",
    "⚡ ¡La disciplina supera a la motivación! Excelente trabajo hoy.",
    "💪 El dolor de hoy será tu fuerza de mañana. ¡Sigue así!",
    "🏆 Cada repetición suma. ¡Has cumplido con tu objetivo diario!",
    "🦁 La constancia es lo que diferencia a los mejores. ¡Gran entreno!"
]

FRASES_SEMANALES = [
    "🚀 'Un día más es un día menos'. ¡Arrancamos un nuevo ciclo con todo!",
    "🏆 Semana nueva, metas más altas. ¡A superar lo de la semana pasada!",
    "⚡ La constancia de la semana pasada es la gasolina de hoy. ¡A darle!",
    "🔥 Nadie te regala nada. ¡Sigue construyendo tu mejor versión!"
]

@student_bp.route('/portal')
def portal():
    if session.get('role') != 'student_custom':
        flash('Debes iniciar sesión como alumno personalizado.', 'warning')
        return redirect(url_for('auth.login'))
        
    student = User.query.get_or_404(session.get('user_id'))
    hoy = datetime.now().date()
    
    # Bloqueo si la membresía caducó
    if student.fecha_vencimiento and student.fecha_vencimiento < hoy:
        session.clear()
        flash(f'Tu membresía venció el {student.fecha_vencimiento}. Por favor acude a recepción para renovarla.', 'danger')
        return redirect(url_for('auth.login'))

    # DETECCIÓN INTELIGENTE DE NUEVA SEMANA (Anti-pendejos)
    semana_iso = hoy.isocalendar()[1]
    resumen_semana_anterior = None
    
    if student.semana_actual_num != semana_iso:
        student.dias_semana_anterior = student.dias_entrenados_semana
        resumen_semana_anterior = {
            'dias_entrenados': student.dias_semana_anterior,
            'mensaje': random.choice(FRASES_SEMANALES)
        }
        student.dias_entrenados_semana = 0
        student.semana_actual_num = semana_iso
        
        rutinas_previas = Routine.query.filter_by(student_id=student.id).all()
        for r in rutinas_previas:
            r.completado = False
            r.fecha_completado = None
            
        db.session.commit()

    rutinas = Routine.query.filter_by(student_id=student.id).all()
    orden_dias = {'Lunes': 1, 'Martes': 2, 'Miércoles': 3, 'Jueves': 4, 'Viernes': 5, 'Sábado': 6, 'Domingo': 7}
    
    for r in rutinas:
        r.ejercicios_list = json.loads(r.ejercicios_json) if r.ejercicios_json else []
        r.comidas_list = json.loads(r.comidas_json) if r.comidas_json else []
        r.orden = orden_dias.get(r.dia_semana, 99)
        
    rutinas.sort(key=lambda x: x.orden)
        
    inicio_mes = hoy.replace(day=1)
    asistencias_mes = Attendance.query.filter(
        Attendance.student_id == student.id,
        db.func.date(Attendance.timestamp) >= inicio_mes
    ).count()
        
    return render_template('student/dashboard.html', 
                           student=student, 
                           rutinas=rutinas, 
                           asistencias_mes=asistencias_mes,
                           resumen_semana=resumen_semana_anterior,
                           hoy=hoy)

@student_bp.route('/complete-workout/<int:routine_id>', methods=['POST'])
def complete_workout(routine_id):
    routine = Routine.query.get_or_404(routine_id)
    
    if routine.completado:
        return jsonify({'success': False, 'message': 'Esta rutina ya fue registrada previamente.'}), 400

    routine.completado = True
    routine.fecha_completado = datetime.now()
    
    student = User.query.get(routine.student_id)
    hoy = datetime.now().date()
    
    if student.ultima_racha_fecha != hoy:
        student.racha_dias += 1
        student.dias_entrenados_semana += 1
        student.ultima_racha_fecha = hoy

    db.session.commit()
    
    frase = random.choice(FRASES_DIARIAS)
    
    return jsonify({
        'success': True, 
        'message': frase,
        'racha': student.racha_dias,
        'dias_semana': student.dias_entrenados_semana
    })

@student_bp.route('/test-simular-semana/<int:dias>')
def test_simular_semana(dias):
    student = User.query.get(session.get('user_id'))
    if student:
        student.racha_dias = dias
        student.dias_entrenados_semana = min(dias, 6)
        student.dias_semana_anterior = random.randint(1, 6)
        student.ultima_racha_fecha = datetime.now().date()
        db.session.commit()
        flash(f'🧪 Simulación: Racha forzada a {dias} días.', 'success')
    return redirect(url_for('student.portal'))