import secrets

from flask import Blueprint, request, jsonify, current_app

api_bp = Blueprint("api", __name__, url_prefix="/api")

@api_bp.before_request
def _exigir_token_de_servicio():
    token = current_app.config.get("API_TOKEN") or ""
    if not token:
        return jsonify({"error": "API deshabilitada: configure API_TOKEN"}), 503
    enviado = request.headers.get("X-API-Key", "")
    if not secrets.compare_digest(enviado, token):
        return jsonify({"error": "No autorizado"}), 401

from api import vehiculos, accesos, qr, placas, rostros
