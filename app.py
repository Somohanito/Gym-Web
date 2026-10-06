from flask import Flask, redirect, url_for
from config import Config
from models import db, User
from routes.auth import auth_bp, bcrypt
from routes.admin import admin_bp
from routes.coach import coach_bp
from routes.student import student_bp

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
bcrypt.init_app(app)

# Registrar todos los Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(coach_bp)
app.register_blueprint(student_bp)

with app.app_context():
    db.create_all()
    
    # Crear usuario Admin por defecto
    if not User.query.filter_by(username='admin').first():
        admin = User(
            nombre='Administrador Principal',
            telefono='0000000000',
            role='admin',
            username='admin',
            password_hash=bcrypt.generate_password_hash('admin123').decode('utf-8'),
            qr_code='QR_MASTER_ADMIN_123'
        )
        db.session.add(admin)
        
    # Crear usuario Coach por defecto para pruebas
    if not User.query.filter_by(username='coach').first():
        coach = User(
            nombre='Entrenador Alex',
            telefono='9619876543',
            role='coach',
            username='coach',
            password_hash=bcrypt.generate_password_hash('coach123').decode('utf-8'),
            qr_code='QR_MASTER_COACH_999'
        )
        db.session.add(coach)
        
    db.session.commit()

@app.route('/')
def inicio():
    return redirect(url_for('auth.login'))

if __name__ == '__main__':
    app.run(debug=True)