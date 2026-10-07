from flask import Flask, redirect, url_for
from config import Config
from models import db
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
bcrypt = Bcrypt(app)

# REDIRECCIÓN AUTOMÁTICA DE LA RAÍZ AL LOGIN (Evita el error 404)
@app.route('/')
def index():
    return redirect(url_for('auth.login'))

# INYECTOR GLOBAL DE CONFIGURACIÓN PARA JINJA2
@app.context_processor
def inject_gym_config():
    return dict(
        gym_name=app.config.get('GYM_NAME', 'GymWeb'),
        gym_slogan=app.config.get('GYM_SLOGAN', 'Tu mejor versión empieza hoy'),
        gym_logo=app.config.get('GYM_LOGO_ICON', '⚡')
    )

# Registrar Blueprints
from routes.auth import auth_bp
from routes.admin import admin_bp
from routes.coach import coach_bp
from routes.student import student_bp

app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(coach_bp)
app.register_blueprint(student_bp)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)