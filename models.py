from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    telefono = db.Column(db.String(20), nullable=False)
    
    role = db.Column(db.String(20), nullable=False, default='student_general')
    username = db.Column(db.String(50), unique=True, nullable=True)
    password_hash = db.Column(db.String(255), nullable=True)
    qr_code = db.Column(db.String(100), unique=True, nullable=False)
    
    is_custom_student = db.Column(db.Boolean, default=False)
    fecha_vencimiento = db.Column(db.Date, nullable=True)
    monto_pago = db.Column(db.Float, default=0.0)
    estado_pago = db.Column(db.String(20), default='Al día')
    
    # GAMIFICACIÓN E HISTORIAL DE SEMANAS Y RACHAS
    racha_dias = db.Column(db.Integer, default=0)
    ultima_racha_fecha = db.Column(db.Date, nullable=True)
    dias_entrenados_semana = db.Column(db.Integer, default=0)
    dias_semana_anterior = db.Column(db.Integer, default=0)
    semana_actual_num = db.Column(db.Integer, default=0)
    
    coach_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    
    # RELACIONES CON ELIMINACIÓN EN CASCADA (Evita errores al borrar alumnos)
    attendances = db.relationship('Attendance', backref='student', lazy=True, cascade="all, delete-orphan")
    routines = db.relationship('Routine', backref='student', lazy=True, foreign_keys='Routine.student_id', cascade="all, delete-orphan")

class Attendance(db.Model):
    __tablename__ = 'attendances'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), nullable=False)

class Routine(db.Model):
    __tablename__ = 'routines'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    coach_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    dia_semana = db.Column(db.String(20), nullable=False) # 'Lunes', 'Martes', etc.
    ejercicios_json = db.Column(db.Text, nullable=False)
    comidas_json = db.Column(db.Text, nullable=True)
    completado = db.Column(db.Boolean, default=False)
    fecha_completado = db.Column(db.DateTime, nullable=True)