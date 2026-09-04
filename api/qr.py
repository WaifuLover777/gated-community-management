from flask import jsonify, request
from api import api_bp
from extensions import limiter
from core.reconocimiento import qr as qr_engine
from modules.garita import services

@api_bp.route("/qr/validar", methods=["POST"])
@limiter.limit("30 per minute")
def validar_qr():
    """Valida un QR. Acepta JSON {"contenido": "<texto>"} o multipart con 'imagen'."""
    archivo = request.files.get("imagen")
    if archivo and archivo.filename:
        contenido = qr_engine.leer_qr(archivo.read())
    else:
        data = request.get_json(silent=True) or {}
        contenido = data.get("contenido")

    if not contenido:
        return jsonify({"ok": False, "mensaje": "QR no detectado"}), 200

    res = services.validar_qr(contenido, guardia_id=(request.get_json(silent=True) or {}).get("guardia_id"))
    return jsonify(res), (200 if res["ok"] else 200)
