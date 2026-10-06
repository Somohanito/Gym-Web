import os

class Config:
    # Clave secreta para sesiones y tokens (cambiar en producción)
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'gymweb_secret_key_987654321'
    
    # Base de datos SQLite local para desarrollo
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///gymweb.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False