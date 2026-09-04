from datetime import datetime
from extensions import db
from models import Acceso

def registrar(*, tipo, resultado, observacion=None, placa=None,
              guardia_id=None, residente_id=None, visita_id=None,
              placa_frontal=None, placa_trasera=None, metodo=None,
              confianza=None, foto_evidencia=None):
    acceso = Acceso(
        tipo=tipo, resultado=resultado, observacion=observacion, placa=placa,
        guardia_id=guardia_id, residente_id=residente_id, visita_id=visita_id,
        placa_frontal=placa_frontal, placa_trasera=placa_trasera, metodo=metodo,
        confianza=confianza, foto_evidencia=foto_evidencia,
        fecha_hora=datetime.utcnow(),
    )
    db.session.add(acceso)
    db.session.commit()
    return acceso

def listar(limite=200):
    return Acceso.query.order_by(Acceso.fecha_hora.desc()).limit(limite).all()
