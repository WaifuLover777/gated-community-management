from datetime import datetime, timedelta

from flask import jsonify, request
from api import api_bp
from extensions import db, limiter
from models import Visita
from core.utils import PIN_TTL_HORAS
from modules.accesos import services as accesos_services

@api_bp.route("/accesos/registrar", methods=["POST"])
def registrar_acceso():
    data = request.get_json(silent=True) or {}
    acceso = accesos_services.registrar(
        tipo=data.get("tipo", "entrada"),
        resultado=data.get("resultado", "autorizado"),
        placa=data.get("placa"),
        observacion=data.get("observacion"),
        guardia_id=data.get("guardia_id"),
        residente_id=data.get("residente_id"),
        visita_id=data.get("visita_id"),
    )
    return jsonify({"ok": True, "id": acceso.id}), 201

@api_bp.route("/visitas/validar-pin", methods=["POST"])
@limiter.limit("10 per minute")
def validar_pin():
    data = request.get_json(silent=True) or {}
    pin = (data.get("pin") or "").strip()
    if not pin:
        return jsonify({"valido": False}), 404

    visita = Visita.query.filter_by(pin=pin, estado="pendiente").first()
    if not visita:
        return jsonify({"valido": False}), 404

    limite = datetime.utcnow() - timedelta(hours=PIN_TTL_HORAS)
    if visita.fecha_creacion and visita.fecha_creacion < limite:
        visita.estado = "expirado"
        db.session.commit()
        return jsonify({"valido": False}), 404

    return jsonify({
        "valido": True,
        "visita_id": visita.id,
        "visitante": visita.nombre_visitante,
        "casa": visita.casa.numero,
    })
