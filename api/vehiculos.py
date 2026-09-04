from flask import jsonify
from api import api_bp
from models import Vehiculo, Cuota

@api_bp.route("/vehiculos/buscar-placa/<placa>")
def buscar_placa(placa):
    vehiculo = Vehiculo.query.filter_by(placa=placa.upper()).first()
    if not vehiculo:
        return jsonify({"encontrado": False, "placa": placa.upper()}), 404

    residente = vehiculo.residente
    morosas = Cuota.query.filter(
        Cuota.casa_id == residente.casa_id,
        Cuota.estado.in_(["pendiente", "vencido"]),
    ).count()
    estado = "al_dia" if morosas == 0 else "moroso"

    return jsonify({
        "encontrado": True,
        "placa": vehiculo.placa,
        "vehiculo": {"marca": vehiculo.marca, "modelo": vehiculo.modelo, "color": vehiculo.color},
        "residente": {
            "nombre": residente.nombre,
            "casa": residente.casa.numero,
            "foto": residente.foto,
        },
        "estado_financiero": estado,
        "autorizado": estado == "al_dia",
    })
