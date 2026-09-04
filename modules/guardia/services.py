from datetime import datetime
from sqlalchemy import or_
from sqlalchemy.orm import selectinload
from extensions import db
from models import Casa, Residente, Vehiculo, Visita, Cuota, Novedad
from modules.accesos import services as accesos_services
from core.utils import filtro_casa_cond, guardar_imagen, rango_hoy_utc
from core.validators import limpiar_texto

CATEGORIAS_NOVEDAD = ("general", "incidente", "ronda", "mantenimiento", "emergencia")

def visitas_hoy():
    inicio, fin = rango_hoy_utc()
    visitas = (Visita.query.filter(Visita.fecha_entrada >= inicio,
                                   Visita.fecha_entrada < fin)
               .order_by(Visita.fecha_entrada.desc()).all())
    for v in visitas:
        v.casa_numero = v.casa.numero
        v.manzana = v.casa.manzana
    return visitas

def contar_dentro():
    inicio, fin = rango_hoy_utc()
    return Visita.query.filter(
        Visita.fecha_entrada >= inicio, Visita.fecha_entrada < fin,
        Visita.fecha_salida.is_(None),
    ).count()


def verificar_placa(placa: str):
    if not placa:
        return None
    v = Vehiculo.query.filter(
        Vehiculo.placa == placa.strip().upper()
    ).join(Residente).join(Casa).first()
    return v

def visitas_pendientes():
    visitas = (Visita.query.filter_by(estado="pendiente")
               .order_by(Visita.fecha_creacion.desc()).all())
    for v in visitas:
        v.casa_numero = v.casa.numero
        v.manzana = v.casa.manzana
    return visitas

def autorizar_entrada(visita_id, guardia_id=None):
    v = Visita.query.filter_by(id=visita_id, estado="pendiente").first()
    if not v:
        return None, "Visita no encontrada o ya procesada"
    v.estado = "usado"
    v.fecha_entrada = datetime.utcnow()
    db.session.commit()
    accesos_services.registrar(
        tipo="entrada", resultado="autorizado", placa=v.placa_vehiculo,
        guardia_id=guardia_id, visita_id=v.id,
        observacion=f"Entrada autorizada desde cola — {v.nombre_visitante}",
    )
    from core import notificaciones
    notificaciones.notificar_casa(
        v.casa_id, "Tu visita ingresó",
        f"{v.nombre_visitante} fue autorizado e ingresó a la urbanización.",
        tipo="visita")
    return v, None

def buscar_residentes(filtro=""):
    q = (Residente.query.join(Casa).filter(Residente.activo.is_(True))
         .options(selectinload(Residente.vehiculos)))
    if filtro:
        like = f"%{filtro}%"
        q = q.filter(or_(filtro_casa_cond(filtro), Residente.nombre.like(like),
                         Vehiculo.placa.like(like.upper())))
        q = q.outerjoin(Vehiculo)
    residentes = q.order_by(Casa.manzana, Casa.numero, Residente.nombre).distinct().all()
    for r in residentes:
        r.casa_numero = r.casa.numero
        r.manzana = r.casa.manzana
        r.placas = ", ".join(v.placa for v in r.vehiculos) if r.vehiculos else ""
    return residentes

def comunicados_para_guardia():
    from modules.comunicados import services as com_services
    return com_services.listar(solo_publicados=True)


def listar_novedades(limite=100):
    novedades = (Novedad.query.order_by(Novedad.fecha_hora.desc()).limit(limite).all())
    for n in novedades:
        n.guardia_nombre = n.guardia.nombre if n.guardia else "—"
    return novedades

def obtener_novedad(novedad_id):
    return Novedad.query.get(novedad_id)

def crear_novedad(*, guardia_id, categoria, texto, tipo="novedad",
                  archivo=None, upload_folder=None):
    texto, err = limpiar_texto(texto, campo="detalle", maximo=1000,
                               requerido=True, minimo=3)
    if err:
        return None, err
    if categoria not in CATEGORIAS_NOVEDAD:
        categoria = "general"
    if tipo not in ("novedad", "cambio_turno"):
        tipo = "novedad"
    foto = None
    if archivo and upload_folder:
        foto, err = guardar_imagen(archivo, upload_folder)
        if err:
            return None, err
    novedad = Novedad(guardia_id=guardia_id, categoria=categoria, texto=texto,
                      tipo=tipo, foto=foto, fecha_hora=datetime.utcnow())
    db.session.add(novedad)
    db.session.commit()
    return novedad, None

def actualizar_novedad(novedad_id, *, categoria, texto):
    n = Novedad.query.get(novedad_id)
    if not n:
        return "Novedad no encontrada"
    texto, err = limpiar_texto(texto, campo="detalle", maximo=1000,
                               requerido=True, minimo=3)
    if err:
        return err
    if categoria in CATEGORIAS_NOVEDAD:
        n.categoria = categoria
    n.texto = texto
    db.session.commit()
    return None
