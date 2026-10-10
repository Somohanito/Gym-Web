import os

class Config:
    # 1. IDENTIDAD DEL CLIENTE / GIMNASIO (Fácil de modificar para cada cliente)
    GYM_NAME = os.environ.get('GYM_NAME', 'H&L Sport Gym')
    GYM_SLOGAN = os.environ.get('GYM_SLOGAN', 'Tu mejor versión empieza hoy')
    GYM_LOGO_ICON = os.environ.get('GYM_LOGO_ICON', '❚█══█❚')
    
    # 2. CONFIGURACIÓN DE SEGURIDAD Y BASE DE DATOS
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'gymweb_secret_key_987654321'
    FERNET_KEY = os.environ.get('FERNET_KEY') or 'x_T9kP2mN7qV4wZ8L1rS5uY3eF6gH0jI8aB9c1d2e3f='
    
    # Soporte automático para PostgreSQL (Render/Railway/Heroku) o SQLite local
    db_url = os.environ.get('DATABASE_URL') or 'sqlite:///gymweb.db'
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
        
    SQLALCHEMY_DATABASE_URI = db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False