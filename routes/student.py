from flask import Blueprint, render_template, redirect, url_for, flash, session
from models import db, User, Routine

student_bp = Blueprint('student', __name__, url_prefix='/student')

@student_bp.route('/portal')
def portal():
    if session.get('role') != 'student_custom':
        flash('Debes iniciar sesión como alumno personalizado.', 'warning')
        return redirect(url_for('auth.login'))
        
    student = User.query.get_or_404(session.get('user_id'))
    return render_template('student/dashboard.html', student=student)