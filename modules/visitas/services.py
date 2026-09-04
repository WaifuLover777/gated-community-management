from datetime import datetime
from sqlalchemy import func
from extensions import db
from models import Casa, Visita
from core.validators import validar_datos_visita
from core.utils import filtro_casa_cond
from modules.accesos import services as accesos_services

def listar(filtro_fecha=None, filtro_casa=None):
    q = Visita.query.join(Casa)
    if filtro_fecha:
        q = q.filter(func.date(Visita.fecha_entrada) == filtro_fecha)
    if filtro_casa and filtro_casa.strip():
        q = q.filter(filtro_casa_cond(filtro_casa))
    visitas = q.order_by(Visita.fecha_entrada.desc()).limit(100).all()
    for v in visitas:
        v.casa_numero = v.casa.numero
        v.manzana = v.casa.manzana
    return visitas

def registrar(*, casa_id, nombre_visitante, cedula_visitante, motivo,
              placa_vehiculo, autorizado_por, guardia_id=None):
    if not casa_id or not Casa.query.get(casa_id):
        return "Selecciona una casa válida."
    datos, err = validar_datos_visita(nombre_visitante, cedula_visitante,
                                      placa_vehiculo, motivo)
    if err:
        return err
    visita = Visita(
        casa_id=casa_id, autorizado_por=autorizado_por, estado="usado",
        fecha_entrada=datetime.utcnow(), **datos,
    )
    db.session.add(visita)
    db.session.commit()
    accesos_services.registrar(
        tipo="entrada", resultado="manual", placa=datos["placa_vehiculo"],
        guardia_id=guardia_id, visita_id=visita.id,
        observacion=f"Ingreso de visitante {datos['nombre_visitante']}",
    )
    return None

def registrar_salida(visita_id, guardia_id=None):
    v = Visita.query.get(visita_id)
    if v:
        v.fecha_salida = datetime.utcnow()
        db.session.commit()
        accesos_services.registrar(
            tipo="salida", resultado="manual", placa=v.placa_vehiculo,
            guardia_id=guardia_id, visita_id=v.id,
            observacion=f"Salida de visitante {v.nombre_visitante}",
        )
