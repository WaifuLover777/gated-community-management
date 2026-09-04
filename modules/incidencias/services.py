from datetime import datetime
from extensions import db
from models import Incidencia, Casa
from core.validators import limpiar_texto
from core.utils import guardar_imagen

CATEGORIAS = ("general", "plomeria", "electricidad", "areas_verdes",
              "seguridad", "limpieza", "otro")
ESTADOS = ("abierto", "en_proceso", "resuelto")

def _con_casa(items):
    for i in items:
        if i.casa:
            i.casa_numero = i.casa.numero
            i.manzana = i.casa.manzana
    return items

def listar_de_casa(casa_id):
    items = (Incidencia.query.filter_by(casa_id=casa_id)
             .order_by(Incidencia.fecha_creacion.desc()).all())
    return _con_casa(items)

def listar_todas(estado=None):
    q = Incidencia.query
    if estado in ESTADOS:
        q = q.filter_by(estado=estado)
    items = q.order_by(Incidencia.fecha_creacion.desc()).limit(200).all()
    return _con_casa(items)

def crear(*, casa_id, residente_id, titulo, descripcion, categoria,
          archivo=None, upload_folder=None):
    if not casa_id or not Casa.query.get(casa_id):
        return "Casa no válida."
    titulo, err = limpiar_texto(titulo, campo="título", maximo=120,
                                requerido=True, minimo=3)
    if err:
        return err
    descripcion, err = limpiar_texto(descripcion, campo="descripción", maximo=1000,
                                     requerido=True, minimo=5)
    if err:
        return err
    if categoria not in CATEGORIAS:
        categoria = "general"
    foto = None
    if archivo and upload_folder:
        foto, err = guardar_imagen(archivo, upload_folder)
        if err:
            return err
    db.session.add(Incidencia(
        casa_id=casa_id, residente_id=residente_id, titulo=titulo,
        descripcion=descripcion, categoria=categoria, foto=foto,
        estado="abierto", fecha_creacion=datetime.utcnow(),
        fecha_actualizacion=datetime.utcnow(),
    ))
    db.session.commit()
    return None

def actualizar_estado(incidencia_id, *, estado, respuesta=None):
    i = Incidencia.query.get(incidencia_id)
    if not i:
        return "Incidencia no encontrada"
    if estado not in ESTADOS:
        return "Estado no válido"
    i.estado = estado
    if respuesta is not None:
        resp, err = limpiar_texto(respuesta, campo="respuesta", maximo=1000,
                                  requerido=False)
        if err:
            return err
        i.respuesta = resp
    i.fecha_actualizacion = datetime.utcnow()
    db.session.commit()
    return None
