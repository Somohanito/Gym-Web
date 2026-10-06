from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from models import db, User
from flask_bcrypt import Bcrypt

auth_bp = Blueprint('auth', __name__)
bcrypt = Bcrypt()

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.password_hash and bcrypt.check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['role'] = user.role
            session['nombre'] = user.nombre
            
            # Redirección según el rol del usuario
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

@auth_bp.route('/reset-password-qr', methods=['GET', 'POST'])
def reset_password_qr():
    """Restablece la contraseña escaneando el QR Maestro del Coach/Admin"""
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        master_qr = data.get('master_qr')
        new_password = data.get('new_password')
        
        # Validar si el QR Maestro pertenece a un Admin o Coach
        master_user = User.query.filter_by(qr_code=master_qr).first()
        if not master_user or master_user.role not in ['admin', 'coach']:
            return jsonify({'success': False, 'message': 'QR Maestro no válido o no autorizado'}), 403
            
        student = User.query.filter_by(username=username).first()
        if not student:
            return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404
            
        # Actualizar contraseña
        student.password_hash = bcrypt.generate_password_hash(new_password).decode('utf-8')
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Contraseña actualizada con éxito'})
        
    return render_template('auth/reset_qr.html')