from flask import jsonify, request
from api import api_bp
from extensions import limiter
from modules.garita import services

@api_bp.route("/rostros/identificar", methods=["POST"])
@limiter.limit("60 per minute")
def identificar_rostros():
    """Identifica ocupantes a partir de una imagen (multipart 'imagen')."""
    archivo = request.files.get("imagen")
    if not archivo or not archivo.filename:
        return jsonify({"ok": False, "mensaje": "Falta la imagen"}), 200
    res = services.procesar_rostros(archivo.read(),
                                    guardia_id=request.form.get("guardia_id"))
    return jsonify(res), 200
