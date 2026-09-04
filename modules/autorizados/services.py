from datetime import datetime, date
from extensions import db
from models import Autorizado
from core.validators import limpiar_texto, validar_cedula
from core.utils import generar_token

RELACIONES = ("empleada", "niñera", "chofer", "jardinero", "familiar", "otro")

def listar_de_casa(casa_id):
    return (Autorizado.query.filter_by(casa_id=casa_id)
            .order_by(Autorizado.activo.desc(), Autorizado.nombre).all())

def obtener(autorizado_id, casa_id):
    return Autorizado.query.filter_by(id=autorizado_id, casa_id=casa_id).first()

def _parse_fecha(valor):
    try:
        return date.fromisoformat((valor or "").strip())
    except ValueError:
        return None

def crear(*, casa_id, residente_id, nombre, cedula, relacion,
          vigencia_desde, vigencia_hasta):
    nombre, err = limpiar_texto(nombre, campo="nombre", maximo=120, requerido=True, minimo=3)
    if err:
        return err
    if cedula:
        cedula, err = validar_cedula(cedula, requerido=False)
        if err:
            return err
    if relacion not in RELACIONES:
        relacion = "otro"
    desde = _parse_fecha(vigencia_desde)
    hasta = _parse_fecha(vigencia_hasta)
    if desde and hasta and hasta < desde:
        return "La fecha de fin no puede ser anterior a la de inicio."
    db.session.add(Autorizado(
        casa_id=casa_id, residente_id=residente_id, nombre=nombre, cedula=cedula or None,
        relacion=relacion, token=generar_token(), vigencia_desde=desde,
        vigencia_hasta=hasta, activo=True, creado_en=datetime.utcnow(),
    ))
    db.session.commit()
    return None

def alternar(autorizado_id, casa_id):
    a = obtener(autorizado_id, casa_id)
    if not a:
        return "Autorizado no encontrado"
    a.activo = not a.activo
    db.session.commit()
    return None
