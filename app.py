from flask import Flask, redirect, url_for
from config import Config
from models import db, User
from routes.auth import auth_bp, bcrypt
from routes.admin import admin_bp  # <-- Importar admin_bp

app = Flask(__name__)
app.config.from_object(Config)

# Inicializar extensiones
db.init_app(app)
bcrypt.init_app(app)

# Registrar Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)  # <-- Registrar admin_bp

# Crear tablas y usuario Administrador inicial
with app.app_context():
    db.create_all()
    
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
        db.session.commit()
        print("Usuario admin creado con éxito: admin / admin123")

@app.route('/')
def inicio():
    return redirect(url_for('auth.login'))

if __name__ == '__main__':
    app.run(debug=True)