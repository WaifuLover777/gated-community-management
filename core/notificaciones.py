"""Canal de notificaciones pluggable."""
import logging
import smtplib
from email.mime.text import MIMEText
from datetime import datetime

from flask import current_app
from extensions import db
from models import Notificacion, Residente

log = logging.getLogger("notificaciones")

def _enviar_consola(destino, asunto, mensaje):
    log.info("[NOTIF consola] -> %s | %s: %s", destino or "—", asunto, mensaje)
    return True

def _enviar_email(destino, asunto, mensaje):
    if not destino:
        return False
    cfg = current_app.config
    host = cfg.get("SMTP_HOST")
    if not host:
        log.warning("NOTIF_BACKEND=email pero SMTP_HOST no está configurado; se omite envío.")
        return False
    msg = MIMEText(mensaje, _charset="utf-8")
    msg["Subject"] = asunto
    msg["From"] = cfg.get("SMTP_FROM", "no-reply@urbanizacion.local")
    msg["To"] = destino
    try:
        with smtplib.SMTP(host, cfg.get("SMTP_PORT", 587), timeout=10) as s:
            if cfg.get("SMTP_TLS", True):
                s.starttls()
            if cfg.get("SMTP_USER"):
                s.login(cfg["SMTP_USER"], cfg.get("SMTP_PASSWORD", ""))
            s.send_message(msg)
        return True
    except Exception as e:
        log.error("Error enviando email a %s: %s", destino, e)
        return False

_BACKENDS = {"consola": _enviar_consola, "email": _enviar_email}

def _despachar(destino, asunto, mensaje):
    backend = (current_app.config.get("NOTIF_BACKEND") or "consola").lower()
    fn = _BACKENDS.get(backend, _enviar_consola)
    return fn(destino, asunto, mensaje)

def notificar_residente(residente_id, titulo, mensaje, tipo="info"):
    """Guarda la notificación en la bandeja y la despacha por el backend activo."""
    if not residente_id:
        return None
    db.session.add(Notificacion(
        residente_id=residente_id, titulo=titulo, mensaje=mensaje, tipo=tipo,
        leido=False, creado_en=datetime.utcnow(),
    ))
    db.session.commit()
    res = Residente.query.get(residente_id)
    _despachar(res.email if res else None, titulo, mensaje)
    return True

def notificar_casa(casa_id, titulo, mensaje, tipo="info"):
    """Notifica a todos los residentes activos de una casa."""
    residentes = Residente.query.filter_by(casa_id=casa_id, activo=True).all()
    for r in residentes:
        notificar_residente(r.id, titulo, mensaje, tipo)
    return len(residentes)

def notificar_todos(titulo, mensaje, tipo="info"):
    """Notifica a todos los residentes activos (p. ej. un comunicado)."""
    residentes = Residente.query.filter_by(activo=True).all()
    for r in residentes:
        notificar_residente(r.id, titulo, mensaje, tipo)
    return len(residentes)


def bandeja(residente_id, solo_no_leidas=False, limite=50):
    q = Notificacion.query.filter_by(residente_id=residente_id)
    if solo_no_leidas:
        q = q.filter_by(leido=False)
    return q.order_by(Notificacion.creado_en.desc()).limit(limite).all()

def contar_no_leidas(residente_id):
    return Notificacion.query.filter_by(residente_id=residente_id, leido=False).count()

def marcar_leidas(residente_id):
    Notificacion.query.filter_by(residente_id=residente_id, leido=False).update(
        {"leido": True})
    db.session.commit()
