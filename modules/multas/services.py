from datetime import datetime, date
from extensions import db
from models import Multa, Casa
from core.validators import limpiar_texto, validar_entero

def listar(estado=None):
    q = Multa.query.join(Casa)
    if estado in ("pendiente", "pagada", "anulada"):
        q = q.filter(Multa.estado == estado)
    multas = q.order_by(Multa.creado_en.desc()).limit(300).all()
    for m in multas:
        m.casa_numero = m.casa.numero if m.casa else "—"
        m.manzana = m.casa.manzana if m.casa else ""
    return multas

def multas_de_casa(casa_id, estado=None):
    q = Multa.query.filter_by(casa_id=casa_id)
    if estado:
        q = q.filter_by(estado=estado)
    return q.order_by(Multa.fecha.desc()).all()

def total_pendiente_casa(casa_id):
    multas = Multa.query.filter_by(casa_id=casa_id, estado="pendiente").all()
    return round(sum(m.monto or 0 for m in multas), 2), len(multas)

def crear(*, casa_id, motivo, descripcion, monto):
    if not casa_id or not Casa.query.get(casa_id):
        return "Selecciona una casa válida."
    motivo, err = limpiar_texto(motivo, campo="motivo", maximo=120, requerido=True, minimo=3)
    if err:
        return err
    descripcion, _ = limpiar_texto(descripcion, campo="descripción", maximo=1000)
    try:
        monto = float(str(monto).replace(",", "."))
    except (TypeError, ValueError):
        return "Monto no válido."
    if monto <= 0:
        return "El monto debe ser mayor que 0."
    db.session.add(Multa(
        casa_id=casa_id, motivo=motivo, descripcion=descripcion, monto=round(monto, 2),
        estado="pendiente", fecha=date.today(), creado_en=datetime.utcnow(),
    ))
    db.session.commit()
    return None

def cambiar_estado(multa_id, estado):
    m = Multa.query.get(multa_id)
    if not m:
        return "Multa no encontrada"
    if estado not in ("pendiente", "pagada", "anulada"):
        return "Estado no válido"
    m.estado = estado
    m.fecha_pago = date.today().isoformat() if estado == "pagada" else None
    db.session.commit()
    return None
