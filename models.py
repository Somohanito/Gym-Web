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
    
    # Datos de inicio de sesión (solo para Admin, Coach y Alumno Personalizado)
    username = db.Column(db.String(50), unique=True, nullable=True)
    password_hash = db.Column(db.String(255), nullable=True)
    
    # Código QR único para acceso al gimnasio
    qr_code = db.Column(db.String(100), unique=True, nullable=False)
    
    # Para la Switch [General | Personalizado] sin perder historial
    is_custom_student = db.Column(db.Boolean, default=False)
    
    # Relación con pagos/membresía
    fecha_vencimiento = db.Column(db.Date, nullable=True)
    monto_pago = db.Column(db.Float, default=0.0)
    estado_pago = db.Column(db.String(20), default='Al día') # 'Al día', 'Vencido'
    
    # Coach asignado (si es alumno personalizado)
    coach_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    # Relaciones
    attendances = db.relationship('Attendance', backref='student', lazy=True)
    routines = db.relationship('Routine', backref='student', lazy=True, foreign_keys='Routine.student_id')

class Attendance(db.Model):
    __tablename__ = 'attendances'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), nullable=False) # 'CONCEDIDO' o 'DENEGADO'

class Routine(db.Model):
    __tablename__ = 'routines'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    coach_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    dia_semana = db.Column(db.String(20), nullable=False) # 'Lunes', 'Martes', etc.
    ejercicios_json = db.Column(db.Text, nullable=False) # Guardaremos la lista de ejercicios como JSON
    comidas_json = db.Column(db.Text, nullable=True)     # Guardaremos la dieta como JSON
    completado = db.Column(db.Boolean, default=False)