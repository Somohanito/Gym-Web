import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'gymweb_secret_key_987654321'
    
    # Soporte para PostgreSQL (Render/Railway/Heroku o PostgreSQL local)
    db_url = os.environ.get('DATABASE_URL') or 'sqlite:///gymweb.db'
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
        
    SQLALCHEMY_DATABASE_URI = db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False