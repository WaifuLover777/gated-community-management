from flask import jsonify, request
from api import api_bp
from extensions import limiter
from core.reconocimiento import placas as placa_engine
from modules.garita import services

@api_bp.route("/placas/leer", methods=["POST"])
@limiter.limit("60 per minute")
def leer_placas():
    """Lee placas frontal/trasera y resuelve el acceso."""
    pf = pt = None
    foto = None
    if request.files:
        f = request.files.get("img_frontal")
        t = request.files.get("img_trasera")
        if f and f.filename:
            foto = f.read()
            pf = (placa_engine.leer_placa(foto, pista=f.filename) or {}).get("placa")
        if t and t.filename:
            data = t.read()
            pt = (placa_engine.leer_placa(data, pista=t.filename) or {}).get("placa")
    data = request.get_json(silent=True) or {}
    pf = pf or data.get("placa_frontal")
    pt = pt or data.get("placa_trasera")
    tipo = data.get("tipo") or request.form.get("tipo", "entrada")

    res = services.procesar_placas(placa_frontal=pf, placa_trasera=pt,
                                   tipo=tipo, foto_bytes=foto,
                                   guardia_id=data.get("guardia_id"))
    return jsonify(res), 200
