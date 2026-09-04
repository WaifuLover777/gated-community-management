from datetime import datetime, date
from extensions import db
from models import AreaComun, Reserva
from core.validators import limpiar_texto

def _hora_valida(valor):
    """Acepta 'HH:MM' en 24h. Devuelve la cadena normalizada o None."""
    if len(valor) != 5 or valor[2] != ":":
        return None
    hh, mm = valor[:2], valor[3:]
    if not (hh.isdigit() and mm.isdigit()):
        return None
    if not (0 <= int(hh) <= 23 and 0 <= int(mm) <= 59):
        return None
    return valor


def listar_areas(solo_activas=False):
    q = AreaComun.query
    if solo_activas:
        q = q.filter_by(activo=True)
    return q.order_by(AreaComun.nombre).all()

def obtener_area(area_id):
    return AreaComun.query.get(area_id)

def crear_area(*, nombre, descripcion, hora_apertura, hora_cierre):
    nombre, err = limpiar_texto(nombre, campo="nombre", maximo=80, requerido=True, minimo=2)
    if err:
        return err
    descripcion, _ = limpiar_texto(descripcion, campo="descripción", maximo=255)
    ha = _hora_valida(hora_apertura) or "08:00"
    hc = _hora_valida(hora_cierre) or "22:00"
    if hc <= ha:
        return "La hora de cierre debe ser posterior a la de apertura."
    db.session.add(AreaComun(nombre=nombre, descripcion=descripcion,
                             hora_apertura=ha, hora_cierre=hc, activo=True))
    db.session.commit()
    return None

def alternar_area(area_id):
    a = AreaComun.query.get(area_id)
    if a:
        a.activo = not a.activo
        db.session.commit()


def _parse_fecha(valor):
    try:
        return date.fromisoformat((valor or "").strip())
    except ValueError:
        return None

def hay_solapamiento(area_id, fecha, hora_inicio, hora_fin, excluir_id=None):
    q = Reserva.query.filter(
        Reserva.area_id == area_id,
        Reserva.fecha == fecha,
        Reserva.estado == "confirmada",
        Reserva.hora_inicio < hora_fin,
        Reserva.hora_fin > hora_inicio,
    )
    if excluir_id:
        q = q.filter(Reserva.id != excluir_id)
    return db.session.query(q.exists()).scalar()

def reservas_de_casa(casa_id):
    items = (Reserva.query.filter_by(casa_id=casa_id)
             .order_by(Reserva.fecha.desc(), Reserva.hora_inicio).all())
    for r in items:
        r.area_nombre = r.area.nombre if r.area else "—"
    return items

def reservas_de_area(area_id, desde=None):
    q = Reserva.query.filter_by(area_id=area_id, estado="confirmada")
    if desde:
        q = q.filter(Reserva.fecha >= desde)
    return q.order_by(Reserva.fecha, Reserva.hora_inicio).all()

def crear_reserva(*, area_id, casa_id, residente_id, fecha, hora_inicio, hora_fin):
    area = AreaComun.query.get(area_id)
    if not area or not area.activo:
        return "Área no disponible."
    f = _parse_fecha(fecha)
    if not f:
        return "Fecha no válida."
    if f < date.today():
        return "No puedes reservar en una fecha pasada."
    hi = _hora_valida(hora_inicio)
    hf = _hora_valida(hora_fin)
    if not hi or not hf:
        return "Horario no válido. Usa el formato HH:MM."
    if hf <= hi:
        return "La hora de fin debe ser posterior a la de inicio."
    if hi < area.hora_apertura or hf > area.hora_cierre:
        return f"El área atiende de {area.hora_apertura} a {area.hora_cierre}."
    if hay_solapamiento(area_id, f, hi, hf):
        return "Ese horario ya está reservado para esta área. Elige otro."
    db.session.add(Reserva(
        area_id=area_id, casa_id=casa_id, residente_id=residente_id,
        fecha=f, hora_inicio=hi, hora_fin=hf, estado="confirmada",
        fecha_creacion=datetime.utcnow(),
    ))
    db.session.commit()
    return None

def cancelar_reserva(reserva_id, casa_id):
    r = Reserva.query.filter_by(id=reserva_id, casa_id=casa_id).first()
    if not r:
        return "Reserva no encontrada"
    r.estado = "cancelada"
    db.session.commit()
    return None
