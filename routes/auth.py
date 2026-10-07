from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from models import db, User
from flask_bcrypt import Bcrypt

auth_bp = Blueprint('auth', __name__)
bcrypt = Bcrypt()
from datetime import datetime
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        identifier = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        user = User.query.filter(
            (User.username == identifier) | (User.telefono == identifier)
        ).first()
        
        if user and user.password_hash and bcrypt.check_password_hash(user.password_hash, password):
            # 1. Impedir el acceso a la web si es un alumno general
            if user.role == 'student_general':
                flash('Los alumnos generales solo tienen acceso físico mediante QR. Contacta a la recepción para cambiar a Alumno Personalizado.', 'warning')
                return render_template('auth/login.html')

            # 2. Bloqueo si la membresía está vencida
            hoy = datetime.now().date()
            if user.role == 'student_custom' and user.fecha_vencimiento and user.fecha_vencimiento < hoy:
                flash(f'Tu membresía venció el {user.fecha_vencimiento}. Acude a recepción para renovarla y recuperar acceso a tu plataforma.', 'danger')
                return render_template('auth/login.html')

            session['user_id'] = user.id
            session['role'] = user.role
            session['nombre'] = user.nombre
            
            if user.role == 'admin':
                return redirect(url_for('admin.dashboard'))
            elif user.role == 'coach':
                return redirect(url_for('coach.dashboard'))
            elif user.role == 'student_custom':
                return redirect(url_for('student.portal'))
        
        flash('Usuario o contraseña incorrectos.', 'danger')
    return render_template('auth/login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))

@auth_bp.route('/check-user', methods=['POST'])
def check_user():
    """Valida si el usuario existe antes de activar la cámara para el QR Maestro"""
    data = request.get_json()
    identifier = data.get('username', '').strip()
    
    user = User.query.filter(
        (User.username == identifier) | (User.telefono == identifier)
    ).first()
    
    if not user:
        return jsonify({'exists': False, 'message': 'El usuario o número de teléfono no existe en la base de datos.'}), 404
        
    if user.role == 'student_general':
        return jsonify({'exists': False, 'message': 'Este alumno es "General". Pídele a Recepción que te cambie a "Personalizado" para tener acceso web.'}), 400
        
    return jsonify({'exists': True, 'nombre': user.nombre})

@auth_bp.route('/reset-password-qr', methods=['GET', 'POST'])
def reset_password_qr():
    if request.method == 'POST':
        data = request.get_json()
        identifier = data.get('username', '').strip()
        master_qr = data.get('master_qr', '').strip()
        new_password = data.get('new_password', '').strip()
        
        # 1. Validar si el QR Maestro pertenece a un Admin o Coach
        master_user = User.query.filter_by(qr_code=master_qr).first()
        if not master_user or master_user.role not in ['admin', 'coach']:
            return jsonify({'success': False, 'message': 'QR Maestro no válido o no autorizado'}), 403
            
        # 2. Buscar al usuario por nombre de usuario o por teléfono
        student = User.query.filter(
            (User.username == identifier) | (User.telefono == identifier)
        ).first()
        
        if not student:
            return jsonify({'success': False, 'message': 'Usuario o teléfono no encontrado en el sistema'}), 404
            
        # 3. Guardar la nueva contraseña con Hash encriptado
        student.password_hash = bcrypt.generate_password_hash(new_password).decode('utf-8')
        
        # Si era un usuario sin username, le asignamos su número de teléfono
        if not student.username:
            student.username = student.telefono
            
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Contraseña actualizada con éxito. Ya puedes iniciar sesión.'})
        
    return render_template('auth/reset_qr.html')