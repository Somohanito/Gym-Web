from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    telefono = db.Column(db.String(20), nullable=False)
    
    # Roles: 'admin', 'coach', 'student_custom', 'student_general'
    role = db.Column(db.String(20), nullable=False, default='student_general')
    
    # Credenciales de acceso web
    username = db.Column(db.String(50), unique=True, nullable=True)
    password_hash = db.Column(db.String(255), nullable=True)
    
    # QR del Alumno o QR Maestro del Coach/Admin
    qr_code = db.Column(db.String(100), unique=True, nullable=False)
    
    # Propiedades para Alumnos
    is_custom_student = db.Column(db.Boolean, default=False)
    fecha_vencimiento = db.Column(db.Date, nullable=True)
    monto_pago = db.Column(db.Float, default=0.0)
    estado_pago = db.Column(db.String(20), default='Al día')
    
    # Coach asignado al alumno
    coach_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    # Relaciones
    attendances = db.relationship('Attendance', backref='student', lazy=True)
    routines = db.relationship('Routine', backref='student', lazy=True, foreign_keys='Routine.student_id')

class Attendance(db.Model):
    __tablename__ = 'attendances'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), nullable=False)

class Routine(db.Model):
    __tablename__ = 'routines'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    coach_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    dia_semana = db.Column(db.String(20), nullable=False)
    ejercicios_json = db.Column(db.Text, nullable=False)
    comidas_json = db.Column(db.Text, nullable=True)
    completado = db.Column(db.Boolean, default=False)