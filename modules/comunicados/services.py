from datetime import datetime
from extensions import db
from models import Comunicado
from core.validators import limpiar_texto

TIPOS = ("anuncio", "circular", "urgente", "evento")

def _parse_fecha(valor):
    if not valor:
        return None
    try:
        return datetime.fromisoformat(valor)
    except ValueError:
        return None

def listar(tipo=None, *, solo_publicados=False, limite=None):
    query = Comunicado.query.filter_by(activo=True)
    if tipo:
        query = query.filter_by(tipo=tipo)
    if solo_publicados:
        query = query.filter(Comunicado.fecha_publicacion <= datetime.utcnow())
    query = query.order_by(Comunicado.fecha_publicacion.desc())
    if limite:
        query = query.limit(limite)
    return query.all()

def obtener(comunicado_id):
    return Comunicado.query.get(comunicado_id)

def _validar(titulo, contenido, tipo):
    titulo, err = limpiar_texto(titulo, campo="título", maximo=150, requerido=True, minimo=3)
    if err:
        return None, None, None, err
    contenido, err = limpiar_texto(contenido, campo="contenido", maximo=1000,
                                   requerido=True, minimo=3)
    if err:
        return None, None, None, err
    if tipo not in TIPOS:
        tipo = "anuncio"
    return titulo, contenido, tipo, None

def crear(*, titulo, contenido, tipo, publicado_por, fecha_publicacion=None):
    titulo, contenido, tipo, err = _validar(titulo, contenido, tipo)
    if err:
        return err
    fecha = _parse_fecha(fecha_publicacion) or datetime.utcnow()
    db.session.add(Comunicado(titulo=titulo, contenido=contenido, tipo=tipo,
                              publicado_por=publicado_por, fecha_publicacion=fecha))
    db.session.commit()
    if fecha <= datetime.utcnow():
        from core import notificaciones
        notificaciones.notificar_todos(
            f"Nuevo comunicado: {titulo}", contenido, tipo="comunicado")
    return None

def actualizar(comunicado_id, *, titulo, contenido, tipo, fecha_publicacion=None):
    c = Comunicado.query.get(comunicado_id)
    if not c:
        return "Comunicado no encontrado"
    titulo, contenido, tipo, err = _validar(titulo, contenido, tipo)
    if err:
        return err
    c.titulo, c.contenido, c.tipo = titulo, contenido, tipo
    fecha = _parse_fecha(fecha_publicacion)
    if fecha:
        c.fecha_publicacion = fecha
    db.session.commit()
    return None

def archivar(comunicado_id):
    c = Comunicado.query.get(comunicado_id)
    if c:
        c.activo = False
        db.session.commit()
