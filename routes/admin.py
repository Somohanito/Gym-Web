from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from models import db, User, Routine, Attendance
from datetime import datetime, timedelta
from flask_bcrypt import Bcrypt
import random

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')
bcrypt = Bcrypt()

def admin_required(f):
    def decorated_function(*args, **kwargs):
        if session.get('role') != 'admin':
            flash('Acceso restringido solo para administradores.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    generales = User.query.filter_by(role='student_general').all()
    personalizados = User.query.filter_by(role='student_custom').all()
    
    hoy = datetime.now().date()
    total_alumnos = len(generales) + len(personalizados)
    
    vencidos = 0
    ingresos_totales = 0.0
    all_students = generales + personalizados
    for s in all_students:
        ingresos_totales += (s.monto_pago or 0.0)
        if s.fecha_vencimiento and s.fecha_vencimiento < hoy:
            vencidos += 1
            
    return render_template('admin/dashboard.html', 
                           generales=generales, 
                           personalizados=personalizados,
                           total_alumnos=total_alumnos,
                           vencidos=vencidos,
                           ingresos_totales=ingresos_totales,
                           hoy=hoy)

@admin_bp.route('/create-student', methods=['POST'])
@admin_required
def create_student():
    nombre = request.form.get('nombre', '').strip()
    telefono = request.form.get('telefono', '').strip()
    tipo = request.form.get('tipo_alumno', 'general')
    dias = int(request.form.get('dias_membresia', 30))
    monto = float(request.form.get('monto', 500.0))
    
    if len(telefono) != 10 or not telefono.isdigit():
        flash('El teléfono debe tener 10 dígitos exactos.', 'danger')
        return redirect(url_for('admin.dashboard'))
        
    qr_code = f"GYM-C{random.randint(100000, 999999)}"
    fecha_venc = datetime.now().date() + timedelta(days=dias)
    
    role = 'student_custom' if tipo == 'custom' else 'student_general'
    
    nuevo_alumno = User(
        nombre=nombre,
        telefono=telefono,
        role=role,
        username=telefono if tipo == 'custom' else None,
        password_hash=bcrypt.generate_password_hash("123456").decode('utf-8') if tipo == 'custom' else None,
        qr_code=qr_code,
        is_custom_student=(tipo == 'custom'),
        fecha_vencimiento=fecha_venc,
        monto_pago=monto,
        estado_pago='Al día'
    )
    
    db.session.add(nuevo_alumno)
    db.session.commit()
    flash(f'Alumno {nombre} registrado correctamente.', 'success')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/renew-student/<int:student_id>', methods=['POST'])
@admin_required
def renew_student(student_id):
    student = User.query.get_or_404(student_id)
    dias = int(request.form.get('dias_membresia', 30))
    monto_nuevo = float(request.form.get('monto', 500.0))
    
    hoy = datetime.now().date()
    if student.fecha_vencimiento and student.fecha_vencimiento >= hoy:
        student.fecha_vencimiento += timedelta(days=dias)
    else:
        student.fecha_vencimiento = hoy + timedelta(days=dias)
        
    student.monto_pago = (student.monto_pago or 0.0) + monto_nuevo
    student.estado_pago = 'Al día'
    
    db.session.commit()
    flash(f'Membresía de {student.nombre} renovada por {dias} días (+${monto_nuevo}).', 'success')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/edit-student/<int:student_id>', methods=['POST'])
@admin_required
def edit_student(student_id):
    student = User.query.get_or_404(student_id)
    student.nombre = request.form.get('nombre', '').strip()
    student.telefono = request.form.get('telefono', '').strip()
    
    if student.role == 'student_custom':
        student.username = student.telefono
        
    db.session.commit()
    flash(f'Información de {student.nombre} actualizada correctamente.', 'info')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/delete-student/<int:student_id>', methods=['POST'])
@admin_required
def delete_student(student_id):
    student = User.query.get_or_404(student_id)
    
    Attendance.query.filter_by(student_id=student.id).delete()
    Routine.query.filter_by(student_id=student.id).delete()
    
    db.session.delete(student)
    db.session.commit()
    flash(f'Alumno {student.nombre} eliminado correctamente.', 'success')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/toggle-student-type/<int:student_id>', methods=['POST'])
@admin_required
def toggle_student_type(student_id):
    student = User.query.get_or_404(student_id)
    if student.role == 'student_general':
        student.role = 'student_custom'
        student.is_custom_student = True
        student.username = student.telefono
        if not student.password_hash:
            student.password_hash = bcrypt.generate_password_hash("123456").decode('utf-8')
    else:
        student.role = 'student_general'
        student.is_custom_student = False
        
    db.session.commit()
    flash(f'Tipo de membresía de {student.nombre} actualizado.', 'info')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/simulate-expiration/<int:student_id>/<mode>', methods=['POST'])
@admin_required
def simulate_expiration(student_id, mode):
    student = User.query.get_or_404(student_id)
    hoy = datetime.now().date()
    
    if mode == 'expired':
        student.fecha_vencimiento = hoy - timedelta(days=2)
    elif mode == 'near':
        student.fecha_vencimiento = hoy + timedelta(days=2)
        
    db.session.commit()
    flash(f'Simulación aplicada a {student.nombre}.', 'warning')
    return redirect(url_for('admin.dashboard'))

# --- RUTAS DE GESTIÓN DE PERSONAL Y STAFF ---
@admin_bp.route('/staff', methods=['GET', 'POST'])
@admin_bp.route('/staff-management', methods=['GET', 'POST'])
@admin_required
def staff():
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        telefono = request.form.get('telefono', '').strip()
        role = request.form.get('role', 'coach')
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        qr_code = f"GYM-M{random.randint(100000, 999999)}"
        password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        
        staff_member = User(
            nombre=nombre,
            telefono=telefono,
            role=role,
            username=username,
            password_hash=password_hash,
            qr_code=qr_code
        )
        db.session.add(staff_member)
        db.session.commit()
        flash(f'Miembro de personal {nombre} registrado.', 'success')
        return redirect(url_for('admin.staff'))
        
    staff_members = User.query.filter(User.role.in_(['admin', 'coach'])).all()
    return render_template('admin/staff.html', staff=staff_members)

@admin_bp.route('/staff-management-alias', methods=['GET', 'POST'])
@admin_required
def staff_management():
    return staff()

@admin_bp.route('/create-staff', methods=['POST'])
@admin_required
def create_staff():
    return staff()

@admin_bp.route('/delete-staff/<int:staff_id>', methods=['POST'])
@admin_required
def delete_staff(staff_id):
    staff_member = User.query.get_or_404(staff_id)
    if staff_member.id == session.get('user_id'):
        flash('No puedes eliminar tu propia cuenta de administrador actual.', 'danger')
        return redirect(url_for('admin.staff'))
        
    db.session.delete(staff_member)
    db.session.commit()
    flash('Personal eliminado correctamente.', 'success')
    return redirect(url_for('admin.staff'))

# --- RUTAS DEL ESCÁNER Y CONTROL DE ACCESO QR ---
@admin_bp.route('/scanner')
@admin_bp.route('/access-control')
@admin_required
def scanner():
    return render_template('admin/scanner.html')

@admin_bp.route('/access-control-alias')
@admin_required
def access_control():
    return scanner()

@admin_bp.route('/verify-qr', methods=['POST'])
@admin_required
def verify_qr():
    data = request.get_json()
    qr_code = data.get('qr_code', '').strip()
    
    student = User.query.filter_by(qr_code=qr_code).first()
    if not student:
        return jsonify({'status': 'error', 'message': 'Código QR no reconocido en el sistema.'}), 404
        
    hoy = datetime.now().date()
    is_valid = student.fecha_vencimiento and student.fecha_vencimiento >= hoy
    
    asistencia = Attendance(
        student_id=student.id,
        status='Acceso Permitido' if is_valid else 'Acceso Denegado (Vencido)'
    )
    db.session.add(asistencia)
    db.session.commit()
    
    if is_valid:
        return jsonify({
            'status': 'success',
            'message': f'¡Bienvenido/a {student.nombre}!',
            'nombre': student.nombre,
            'vencimiento': str(student.fecha_vencimiento)
        })
    else:
        return jsonify({
            'status': 'denied',
            'message': f'Acceso denegado: Membresía de {student.nombre} vencida el {student.fecha_vencimiento}.',
            'nombre': student.nombre,
            'vencimiento': str(student.fecha_vencimiento)
        })

# --- RUTAS DE WHATSAPP Y ALERTAS ---
@admin_bp.route('/whatsapp')
@admin_bp.route('/whatsapp-reminders')
@admin_required
def whatsapp():
    hoy = datetime.now().date()
    # Consulta unificada para alumnos a vencer o ya vencidos
    alumnos_alertas = User.query.filter(
        User.role.in_(['student_general', 'student_custom']),
        User.fecha_vencimiento != None,
        User.fecha_vencimiento <= hoy + timedelta(days=3)
    ).all()
    
    return render_template('admin/whatsapp.html', 
                           alumnos=alumnos_alertas, 
                           hoy=hoy)

@admin_bp.route('/whatsapp-reminders-alias')
@admin_required
def whatsapp_reminders():
    return whatsapp()