from datetime import datetime
from extensions import db
from models import Paquete, Casa
from core.validators import limpiar_texto
from core.utils import guardar_imagen
from core import notificaciones

def _con_casa(items):
    for p in items:
        if p.casa:
            p.casa_numero = p.casa.numero
            p.manzana = p.casa.manzana
    return items

def listar(estado=None):
    q = Paquete.query
    if estado in ("recibido", "entregado"):
        q = q.filter_by(estado=estado)
    return _con_casa(q.order_by(Paquete.creado_en.desc()).limit(200).all())

def listar_de_casa(casa_id):
    items = (Paquete.query.filter_by(casa_id=casa_id)
             .order_by(Paquete.creado_en.desc()).all())
    return _con_casa(items)

def registrar(*, casa_id, descripcion, remitente, recibido_por,
              archivo=None, upload_folder=None):
    if not casa_id or not Casa.query.get(casa_id):
        return "Selecciona una casa válida."
    descripcion, err = limpiar_texto(descripcion, campo="descripción", maximo=200,
                                     requerido=True, minimo=2)
    if err:
        return err
    remitente, _ = limpiar_texto(remitente, campo="remitente", maximo=120)
    foto = None
    if archivo and upload_folder:
        foto, err = guardar_imagen(archivo, upload_folder)
        if err:
            return err
    db.session.add(Paquete(
        casa_id=casa_id, descripcion=descripcion, remitente=remitente, foto=foto,
        estado="recibido", recibido_por=recibido_por, creado_en=datetime.utcnow(),
    ))
    db.session.commit()
    notificaciones.notificar_casa(
        casa_id, "Tienes un paquete en garita",
        f"Llegó un paquete: {descripcion}." + (f" Remitente: {remitente}." if remitente else ""),
        tipo="info")
    return None

def marcar_entregado(paquete_id, retirado_por=None):
    p = Paquete.query.get(paquete_id)
    if not p:
        return "Paquete no encontrado"
    p.estado = "entregado"
    p.retirado_por = (retirado_por or "").strip() or None
    p.fecha_entrega = datetime.utcnow()
    db.session.commit()
    return None
