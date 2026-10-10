from cryptography.fernet import Fernet
import os

# Clave estática para cifrado de datos sensibles
SECRET_KEY_FERNET = os.environ.get('FERNET_KEY', 'x_T9kP2mN7qV4wZ8L1rS5uY3eF6gH0jI8aB9c1d2e3f=')
cipher = Fernet(SECRET_KEY_FERNET.encode() if len(SECRET_KEY_FERNET) == 44 else Fernet.generate_key())

def encriptar_dato(texto: str) -> str:
    if not texto: return ""
    try:
        return cipher.encrypt(texto.encode()).decode()
    except Exception:
        return texto

def desencriptar_dato(texto_cifrado: str) -> str:
    if not texto_cifrado: return ""
    try:
        return cipher.decrypt(texto_cifrado.encode()).decode()
    except Exception:
        return texto_cifrado