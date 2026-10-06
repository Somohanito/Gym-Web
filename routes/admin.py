from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import db, User
from datetime import datetime, timedelta
import uuid

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    def decorated_function(*args, **kwargs):
        if session.get('role') != 'admin':
            flash('Acceso no autorizado.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    generales = User.query.filter_by(is_custom_student=False, role='student_general').all()
    personalizados = User.query.filter_by(is_custom_student=True).all()
    
    # KPIs rápidos
    total_alumnos = len(generales) + len(personalizados)
    vencidos = User.query.filter(User.estado_pago == 'Vencido').count()
    
    return render_template('admin/dashboard.html', 
                           generales=generales, 
                           personalizados=personalizados,
                           total_alumnos=total_alumnos,
                           vencidos=vencidos)

@admin_bp.route('/student/create', methods=['POST'])
@admin_required
def create_student():
    nombre = request.form.get('nombre')
    telefono = request.form.get('telefono')
    tipo_alumno = request.form.get('tipo_alumno')
    dias_membresia = int(request.form.get('dias_membresia', 30))
    monto = float(request.form.get('monto', 0.0))
    
    qr_code = f"GYM-{uuid.uuid4().hex[:8].upper()}"
    fecha_vencimiento = datetime.now().date() + timedelta(days=dias_membresia)
    
    is_custom = True if tipo_alumno == 'custom' else False
    role = 'student_custom' if is_custom else 'student_general'
    username = telefono if is_custom else None
    
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
    flash('Alumno registrado con éxito.', 'success')
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