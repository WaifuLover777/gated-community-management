"""Lectura y generación de códigos QR."""
import io

from flask import current_app
from itsdangerous import URLSafeSerializer, BadSignature

PREFIJO_VISITA = "URBVIS:"
PREFIJO_RESIDENTE = "URBRES:"
PREFIJO_AUTORIZADO = "URBAUT:"
_SALT_RESIDENTE = "qr-residente"


def leer_qr(imagen_bytes):
    """Devuelve el texto del primer QR detectado en la imagen, o None."""
    import cv2
    import numpy as np
    arr = np.frombuffer(imagen_bytes, dtype=np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None:
        return None
    detector = cv2.QRCodeDetector()
    texto, puntos, _ = detector.detectAndDecode(img)
    return texto or None


def png_bytes(texto):
    import qrcode
    img = qrcode.make(texto)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

def png_visita(token):
    return png_bytes(PREFIJO_VISITA + token)

def png_residente(residente_id):
    return png_bytes(PREFIJO_RESIDENTE + firmar_residente(residente_id))

def png_autorizado(token):
    return png_bytes(PREFIJO_AUTORIZADO + token)


def _serializer():
    return URLSafeSerializer(current_app.config["SECRET_KEY"], salt=_SALT_RESIDENTE)

def firmar_residente(residente_id):
    return _serializer().dumps(int(residente_id))

def verificar_residente(firma):
    try:
        return _serializer().loads(firma)
    except (BadSignature, ValueError, TypeError):
        return None
