from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify, send_file
from models import db, User, Routine, Attendance
from datetime import datetime, timedelta
from flask_bcrypt import Bcrypt
from utils.security import encriptar_dato, desencriptar_dato
import random
import pandas as pd
from io import BytesIO

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
    coaches = User.query.filter_by(role='coach').all()
    
    for u in generales + personalizados:
        u.telefono_desencriptado = desencriptar_dato(u.telefono)
        
    hoy = datetime.now().date()
    total_alumnos = len(generales) + len(personalizados)
    
    vencidos = 0
    ingresos_efectivo = 0.0
    ingresos_transferencia = 0.0
    
    for s in generales + personalizados:
        monto = (s.monto_pago or 0.0)
        if getattr(s, 'metodo_pago', 'Efectivo') == 'Transferencia':
            ingresos_transferencia += monto
        else:
            ingresos_efectivo += monto
            
        if s.fecha_vencimiento and s.fecha_vencimiento < hoy:
            vencidos += 1
            
    ingresos_totales = ingresos_efectivo + ingresos_transferencia
            
    return render_template('admin/dashboard.html', 
                           generales=generales, 
                           personalizados=personalizados,
                           coaches=coaches,
                           total_alumnos=total_alumnos,
                           vencidos=vencidos,
                           ingresos_totales=ingresos_totales,
                           ingresos_efectivo=ingresos_efectivo,
                           ingresos_transferencia=ingresos_transferencia,
                           hoy=hoy)

@admin_bp.route('/create-student', methods=['POST'])
@admin_required
def create_student():
    nombre = request.form.get('nombre', '').strip()
    telefono = request.form.get('telefono', '').strip()
    tipo = request.form.get('tipo_alumno', 'general')
    dias = int(request.form.get('dias_membresia', 30))
    monto = float(request.form.get('monto', 500.0))
    metodo_pago = request.form.get('metodo_pago', 'Efectivo')
    coach_id = request.form.get('coach_id')
    
    qr_code = f"GYM-C{random.randint(100000, 999999)}"
    fecha_venc = datetime.now().date() + timedelta(days=dias)
    role = 'student_custom' if tipo == 'custom' else 'student_general'
    
    nuevo_alumno = User(
        nombre=nombre,
        telefono=encriptar_dato(telefono),
        role=role,
        username=telefono if tipo == 'custom' else None,
        password_hash=bcrypt.generate_password_hash("123456").decode('utf-8') if tipo == 'custom' else None,
        qr_code=qr_code,
        is_custom_student=(tipo == 'custom'),
        fecha_vencimiento=fecha_venc,
        monto_pago=monto,
        metodo_pago=metodo_pago,
        estado_pago='Al día',
        coach_id=int(coach_id) if coach_id and tipo == 'custom' else None
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
    metodo_pago = request.form.get('metodo_pago', 'Efectivo')
    
    hoy = datetime.now().date()
    if student.fecha_vencimiento and student.fecha_vencimiento >= hoy:
        student.fecha_vencimiento += timedelta(days=dias)
    else:
        student.fecha_vencimiento = hoy + timedelta(days=dias)
        
    student.monto_pago = (student.monto_pago or 0.0) + monto_nuevo
    student.metodo_pago = metodo_pago
    student.estado_pago = 'Al día'
    db.session.commit()
    flash(f'Membresía renovada con éxito.', 'success')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/edit-student/<int:student_id>', methods=['POST'])
@admin_required
def edit_student(student_id):
    student = User.query.get_or_404(student_id)
    student.nombre = request.form.get('nombre', '').strip()
    tel = request.form.get('telefono', '').strip()
    student.telefono = encriptar_dato(tel)
    
    tipo = request.form.get('tipo_alumno', 'general')
    coach_id = request.form.get('coach_id')
    
    if tipo == 'custom':
        student.role = 'student_custom'
        student.is_custom_student = True
        student.username = tel
        student.coach_id = int(coach_id) if coach_id else None
        if not student.password_hash:
            student.password_hash = bcrypt.generate_password_hash("123456").decode('utf-8')
    else:
        student.role = 'student_general'
        student.is_custom_student = False
        student.coach_id = None
        
    db.session.commit()
    flash(f'Información y plan de {student.nombre} actualizados.', 'info')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/delete-student/<int:student_id>', methods=['POST'])
@admin_required
def delete_student(student_id):
    student = User.query.get_or_404(student_id)
    db.session.delete(student)
    db.session.commit()
    flash(f'Alumno eliminado.', 'success')
    return redirect(url_for('admin.dashboard'))

# EXCEL EXCLUSIVO DE INGRESOS Y CONTABILIDAD DESDE EL DASHBOARD
@admin_bp.route('/export-excel')
@admin_required
def export_excel():
    alumnos = User.query.filter(User.role.in_(['student_general', 'student_custom'])).all()
    hoy = datetime.now().date()
    activos_data, vencidos_data = [], []

    for a in alumnos:
        item = {
            'ID': a.id,
            'Nombre': a.nombre,
            'Teléfono': desencriptar_dato(a.telefono),
            'Tipo': 'Personalizado' if a.is_custom_student else 'General',
            'Monto Pagado ($)': getattr(a, 'monto_pago', 0),
            'Método Pago': getattr(a, 'metodo_pago', 'Efectivo'),
            'Vencimiento': a.fecha_vencimiento
        }
        if a.fecha_vencimiento and a.fecha_vencimiento < hoy:
            vencidos_data.append(item)
        else:
            activos_data.append(item)

    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        pd.DataFrame(activos_data).to_excel(writer, sheet_name='Ingresos Alumnos Activos', index=False)
        pd.DataFrame(vencidos_data).to_excel(writer, sheet_name='Alumnos Vencidos', index=False)
    
    output.seek(0)
    return send_file(output, download_name=f"Reporte_Ingresos_{hoy}.xlsx", as_attachment=True)

# EXCEL EXCLUSIVO DE ACCESOS Y ENTRADAS DESDE CONTROL DE ACCESO
@admin_bp.route('/export-access-excel')
@admin_required
def export_access_excel():
    hoy = datetime.now().date()
    asistencias = Attendance.query.order_by(Attendance.timestamp.desc()).all()
    accesos_data = []

    for asc in asistencias:
        accesos_data.append({
            'Fecha y Hora': asc.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'Nombre de Alumno': asc.student.nombre if asc.student else 'Desconocido',
            'Teléfono': desencriptar_dato(asc.student.telefono) if asc.student else 'N/A',
            'Estado del Acceso': asc.status
        })

    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        pd.DataFrame(accesos_data).to_excel(writer, sheet_name='Historial de Accesos', index=False)
    
    output.seek(0)
    return send_file(output, download_name=f"Reporte_Accesos_Entradas_{hoy}.xlsx", as_attachment=True)

@admin_bp.route('/staff', methods=['GET', 'POST'])
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
        
        nuevo_staff = User(
            nombre=nombre, telefono=encriptar_dato(telefono), role=role,
            username=username, password_hash=password_hash, qr_code=qr_code
        )
        db.session.add(nuevo_staff)
        db.session.commit()
        flash(f'Usuario {nombre} registrado.', 'success')
        return redirect(url_for('admin.staff'))
        
    staff_members = User.query.filter(User.role.in_(['admin', 'coach'])).all()
    for s in staff_members:
        s.telefono_desencriptado = desencriptar_dato(s.telefono)
        
    current_user = User.query.get(session.get('user_id'))
    return render_template('admin/staff.html', staff=staff_members, current_user=current_user)

@admin_bp.route('/delete-staff/<int:staff_id>', methods=['POST'])
@admin_required
def delete_staff(staff_id):
    staff_member = User.query.get_or_404(staff_id)
    if staff_member.id == session.get('user_id'):
        flash('No puedes eliminar tu propia cuenta.', 'danger')
        return redirect(url_for('admin.staff'))
        
    db.session.delete(staff_member)
    db.session.commit()
    flash('Usuario eliminado correctamente.', 'success')
    return redirect(url_for('admin.staff'))

@admin_bp.route('/scanner')
@admin_bp.route('/access-control')
@admin_required
def access_control():
    hoy = datetime.now().date()
    hoy_start = datetime.combine(hoy, datetime.min.time())
    
    # 1. Asistencias estrictamente de HOY para la tabla y la gráfica de horas
    asistencias_hoy = Attendance.query.filter(Attendance.timestamp >= hoy_start).order_by(Attendance.timestamp.desc()).all()
    
    # Gráfica de HORAS: Se calcula únicamente con las entradas de HOY (se resetea al día)
    horas_dict = {str(i).zfill(2)+":00": 0 for i in range(5, 24)}
    for a in asistencias_hoy:
        hora_str = a.timestamp.strftime('%H:00')
        if hora_str in horas_dict:
            horas_dict[hora_str] += 1
            
    # Gráfica de DÍAS: Se calcula con el acumulado de la semana actual (Lunes a Domingo)
    inicio_semana = hoy - timedelta(days=hoy.weekday()) # Lunes de esta semana
    inicio_semana_dt = datetime.combine(inicio_semana, datetime.min.time())
    asistencias_semana = Attendance.query.filter(Attendance.timestamp >= inicio_semana_dt).all()
    
    dias_dict = {'Lunes': 0, 'Martes': 0, 'Miércoles': 0, 'Jueves': 0, 'Viernes': 0, 'Sábado': 0, 'Domingo': 0}
    dias_map = {0: 'Lunes', 1: 'Martes', 2: 'Miércoles', 3: 'Jueves', 4: 'Viernes', 5: 'Sábado', 6: 'Domingo'}
    
    for a in asistencias_semana:
        dia_nombre = dias_map[a.timestamp.weekday()]
        dias_dict[dia_nombre] += 1
        
    return render_template('admin/scanner.html', 
                           asistencias=asistencias_hoy, 
                           horas_labels=list(horas_dict.keys()), 
                           horas_data=list(horas_dict.values()),
                           dias_labels=list(dias_dict.keys()), 
                           dias_data=list(dias_dict.values()))

@admin_bp.route('/verify-qr', methods=['POST'])
@admin_required
def verify_qr():
    data = request.get_json()
    qr_code = data.get('qr_code', '').strip()
    student = User.query.filter_by(qr_code=qr_code).first()
    if not student:
        return jsonify({'status': 'error', 'message': 'Código QR no reconocido.'}), 404
        
    hoy = datetime.now().date()
    is_valid = student.fecha_vencimiento and student.fecha_vencimiento >= hoy
    estado_acceso = 'CONCEDIDO' if is_valid else 'DENEGADO'
    
    asistencia = Attendance(student_id=student.id, status=estado_acceso)
    db.session.add(asistencia)
    db.session.commit()
    
    return jsonify({
        'status': estado_acceso,
        'nombre': student.nombre,
        'vencimiento': str(student.fecha_vencimiento) if is_valid else 'Membresía Vencida'
    })