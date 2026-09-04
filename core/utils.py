import os
import secrets
import uuid
from datetime import datetime, timedelta

MESES = ["", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
         "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

PIN_TTL_HORAS = 24

TZ_OFFSET_HORAS = int(os.environ.get("TZ_OFFSET_HORAS", "-5"))

def rango_hoy_utc():
    """Inicio (incl.) y fin (excl.) del día local de HOY, en UTC.

    Las visitas se guardan con datetime.utcnow(); comparar contra date.today()
    (local) las oculta después de las 19:00 en Ecuador (UTC-5).
    """
    ahora_local = datetime.utcnow() + timedelta(hours=TZ_OFFSET_HORAS)
    inicio_local = ahora_local.replace(hour=0, minute=0, second=0, microsecond=0)
    inicio_utc = inicio_local - timedelta(hours=TZ_OFFSET_HORAS)
    return inicio_utc, inicio_utc + timedelta(days=1)

def generar_token():
    """Token aleatorio url-safe para invitaciones (QR)."""
    return secrets.token_urlsafe(16)

IMAGENES_PERMITIDAS = {"jpg", "jpeg", "png"}

def generar_pin():
    return f"{secrets.randbelow(1_000_000):06d}"

def guardar_imagen(archivo, upload_folder, *, permitidas=IMAGENES_PERMITIDAS):
    """Guarda una imagen subida con nombre único. Devuelve (nombre, error)."""
    if not archivo or not archivo.filename:
        return None, None
    ext = archivo.filename.rsplit(".", 1)[-1].lower() if "." in archivo.filename else ""
    if ext not in permitidas:
        return None, "Formato de imagen no permitido. Usa JPG o PNG."
    nombre = f"{uuid.uuid4().hex}.{ext}"
    archivo.save(os.path.join(upload_folder, nombre))
    return nombre, None

def filtro_casa_cond(term):
    from sqlalchemy import or_, func
    from models import Casa
    like = f"%{(term or '').strip()}%"

    nombre_completo = (func.coalesce(Casa.manzana, "")
                       .op("||")("-")
                       .op("||")(func.coalesce(Casa.numero, "")))
    return or_(
        Casa.numero.ilike(like),
        Casa.manzana.ilike(like),
        nombre_completo.ilike(like),
    )

def fmt_dt(value, fmt="%Y-%m-%d %H:%M"):
    if value is None:
        return ""
    try:
        local = value + timedelta(hours=TZ_OFFSET_HORAS)
        return local.strftime(fmt)
    except (AttributeError, TypeError):
        return str(value)[:16]
