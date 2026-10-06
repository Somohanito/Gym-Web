from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from models import db, User, Attendance
from datetime import datetime, timedelta
import uuid
import re

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    def decorated_function(*args, **kwargs):
        if session.get('role') != 'admin':
            flash('Acceso no autorizado. Se requieren permisos de Administrador.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    generales = User.query.filter_by(is_custom_student=False, role='student_general').all()
    personalizados = User.query.filter_by(is_custom_student=True).all()
    coaches = User.query.filter_by(role='coach').all()
    
    total_alumnos = len(generales) + len(personalizados)
    hoy = datetime.now().date()
    vencidos = User.query.filter(User.fecha_vencimiento < hoy, User.role.in_(['student_general', 'student_custom'])).count()
    
    return render_template('admin/dashboard.html', 
                           generales=generales, 
                           personalizados=personalizados,
                           coaches=coaches,
                           total_alumnos=total_alumnos,
                           vencidos=vencidos,
                           hoy=hoy)

@admin_bp.route('/student/create', methods=['POST'])
@admin_required
def create_student():
    nombre = request.form.get('nombre')
    telefono = request.form.get('telefono', '').strip()
    tipo_alumno = request.form.get('tipo_alumno')
    dias_membresia = int(request.form.get('dias_membresia', 30))
    monto = float(request.form.get('monto', 0.0))
    
    # Validar que el teléfono sean solo 10 dígitos numéricos
    if not re.match(r'^\d{10}$', telefono):
        flash('El número de teléfono debe contener exactamente 10 dígitos numéricos.', 'danger')
        return redirect(url_for('admin.dashboard'))
    
    qr_code = f"GYM-{uuid.uuid4().hex[:8].upper()}"
    fecha_vencimiento = datetime.now().date() + timedelta(days=dias_membresia)
    
    is_custom = True if tipo_alumno == 'custom' else False
    role = 'student_custom' if is_custom else 'student_general'
    username = telefono if is_custom else None
    
    # Verificar usuario duplicado
    if is_custom and User.query.filter_by(username=username).first():
        flash('Ya existe un alumno registrado con ese número de teléfono.', 'warning')
        return redirect(url_for('admin.dashboard'))

    new_student = User(
        nombre=nombre,
        telefono=telefono,
        role=role,
        username=username,
        qr_code=qr_code,
        is_custom_student=is_custom,
        fecha_vencimiento=fecha_vencimiento,
        monto_pago=monto,
        estado_pago='Al día'
    )
    
    db.session.add(new_student)
    db.session.commit()
    flash(f'Alumno {nombre} registrado con éxito con el código QR: {qr_code}', 'success')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/student/delete/<int:student_id>', methods=['POST'])
@admin_required
def delete_student(student_id):
    """Elimina permanentemente a un alumno"""
    student = User.query.get_or_404(student_id)
    # Eliminar asistencias asociadas
    Attendance.query.filter_by(student_id=student.id).delete()
    db.session.delete(student)
    db.session.commit()
    flash('Alumno eliminado del sistema correctamente.', 'info')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/student/toggle-type/<int:student_id>', methods=['POST'])
@admin_required
def toggle_student_type(student_id):
    student = User.query.get_or_404(student_id)
    if student.is_custom_student:
        student.is_custom_student = False
        student.role = 'student_general'
    else:
        student.is_custom_student = True
        student.role = 'student_custom'
        if not student.username:
            student.username = student.telefono
            
    db.session.commit()
    flash(f'Membresía de {student.nombre} actualizada correctamente.', 'info')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/student/simulate-expiration/<int:student_id>/<string:mode>', methods=['POST'])
@admin_required
def simulate_expiration(student_id, mode):
    """Herramienta de prueba para Admin: cambia la fecha a vencida o por vencer"""
    student = User.query.get_or_404(student_id)
    hoy = datetime.now().date()
    
    if mode == 'expired':
        student.fecha_vencimiento = hoy - timedelta(days=2)
        student.estado_pago = 'Vencido'
    elif mode == 'near':
        student.fecha_vencimiento = hoy + timedelta(days=2)
        student.estado_pago = 'Al día'
    elif mode == 'reset':
        student.fecha_vencimiento = hoy + timedelta(days=30)
        student.estado_pago = 'Al día'
        
    db.session.commit()
    flash(f'Fecha de {student.nombre} actualizada para pruebas ({student.fecha_vencimiento}).', 'secondary')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/access-control')
@admin_required
def access_control():
    """Control de Acceso QR en Recepción"""
    today = datetime.now().date()
    asistencias = Attendance.query.filter(
        db.func.date(Attendance.timestamp) == today
    ).order_by(Attendance.timestamp.desc()).limit(10).all()
    
    return render_template('admin/scanner.html', asistencias=asistencias)

@admin_bp.route('/validate-qr', methods=['POST'])
@admin_required
def validate_qr():
    data = request.get_json()
    qr_code = data.get('qr_code')
    
    student = User.query.filter_by(qr_code=qr_code).first()
    
    if not student:
        return jsonify({
            'success': False, 
            'status': 'DENEGADO',
            'message': 'Código QR No Registrado ❌'
        }), 404
        
    hoy = datetime.now().date()
    es_valido = student.fecha_vencimiento and student.fecha_vencimiento >= hoy
    status_str = 'CONCEDIDO' if es_valido else 'DENEGADO'
    
    registro = Attendance(
        student_id=student.id,
        status=status_str
    )
    db.session.add(registro)
    
    if not es_valido:
        student.estado_pago = 'Vencido'
        
    db.session.commit()
    
    if es_valido:
        return jsonify({
            'success': True,
            'status': 'CONCEDIDO',
            'nombre': student.nombre,
            'vencimiento': student.fecha_vencimiento.strftime('%d/%m/%Y'),
            'message': f'¡Bienvenido(a), {student.nombre}! Acceso Autorizado 🟢'
        })
    else:
        return jsonify({
            'success': False,
            'status': 'DENEGADO',
            'nombre': student.nombre,
            'vencimiento': student.fecha_vencimiento.strftime('%d/%m/%Y'),
            'message': f'Mensualidad Vencida ({student.fecha_vencimiento.strftime("%d/%m/%Y")}) 🔴'
        })

@admin_bp.route('/whatsapp-reminders')
@admin_required
def whatsapp_reminders():
    hoy = datetime.now().date()
    limite_proximo = hoy + timedelta(days=3)
    
    alumnos_notificar = User.query.filter(
        User.role.in_(['student_general', 'student_custom']),
        User.fecha_vencimiento <= limite_proximo
    ).order_by(User.fecha_vencimiento.asc()).all()
    
    return render_template('admin/whatsapp.html', alumnos=alumnos_notificar, hoy=hoy)