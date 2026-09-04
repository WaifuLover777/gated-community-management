import os
from datetime import timedelta
from decouple import config as env

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)
UPLOAD_DIR = os.path.join(BASE_DIR, "static", "comprobantes")
os.makedirs(UPLOAD_DIR, exist_ok=True)
for _sub in ("camaras/frontal", "camaras/trasera", "camaras/cabina"):
    os.makedirs(os.path.join(DATA_DIR, _sub), exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, "static", "evidencia"), exist_ok=True)

class Config:
    SECRET_KEY = env("SECRET_KEY", default=None)
    SQLALCHEMY_DATABASE_URI = env(
        "DATABASE_URL",
        default="sqlite:///" + os.path.join(DATA_DIR, "urbanizacion.db"),
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = env("FLASK_DEBUG", default=False, cast=bool)

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"

    SESSION_COOKIE_SECURE = env("SESSION_COOKIE_SECURE", default=False, cast=bool)
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)
    UPLOAD_FOLDER = UPLOAD_DIR
    MAX_CONTENT_LENGTH = 25 * 1024 * 1024

    API_TOKEN = env("API_TOKEN", default="")

    RECARGO_MORA_MENSUAL = env("RECARGO_MORA_MENSUAL", default=0.10, cast=float)

    NOTIF_BACKEND = env("NOTIF_BACKEND", default="consola")
    SMTP_HOST = env("SMTP_HOST", default="")
    SMTP_PORT = env("SMTP_PORT", default=587, cast=int)
    SMTP_TLS = env("SMTP_TLS", default=True, cast=bool)
    SMTP_USER = env("SMTP_USER", default="")
    SMTP_PASSWORD = env("SMTP_PASSWORD", default="")
    SMTP_FROM = env("SMTP_FROM", default="no-reply@urbanizacion.local")

    CAMARAS_DIR = os.path.join(DATA_DIR, "camaras")
    EVIDENCIA_DIR = os.path.join(BASE_DIR, "static", "evidencia")

    CAMARA_FRONTAL_BACKEND = env("CAMARA_FRONTAL_BACKEND", default="emulador_archivo")
    CAMARA_FRONTAL_URL = env("CAMARA_FRONTAL_URL", default="")
    CAMARA_TRASERA_BACKEND = env("CAMARA_TRASERA_BACKEND", default="emulador_archivo")
    CAMARA_TRASERA_URL = env("CAMARA_TRASERA_URL", default="")
    CAMARA_CABINA_BACKEND = env("CAMARA_CABINA_BACKEND", default="emulador_archivo")
    CAMARA_CABINA_URL = env("CAMARA_CABINA_URL", default="")

    RECOG_PLACA_BACKEND = env("RECOG_PLACA_BACKEND", default="sim")
    RECOG_ROSTRO_BACKEND = env("RECOG_ROSTRO_BACKEND", default="sim")
    RECOG_ROSTRO_UMBRAL = env("RECOG_ROSTRO_UMBRAL", default=0.45, cast=float)
    PLATERECOGNIZER_TOKEN = env("PLATERECOGNIZER_TOKEN", default="")
    EVIDENCIA_RETENCION_DIAS = env("EVIDENCIA_RETENCION_DIAS", default=30, cast=int)
