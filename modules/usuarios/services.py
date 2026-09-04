from sqlalchemy.exc import IntegrityError
from extensions import db
from models import Usuario, Residente, Acceso, Novedad
from core.validators import validar_nombre, validar_email, validar_password

ROLES_VALIDOS = ("admin", "guardia", "residente")

def listar():
    usuarios = Usuario.query.order_by(Usuario.rol, Usuario.nombre).all()
    for u in usuarios:
        u.residente_nombre = u.residente.nombre if u.residente else None
    return usuarios

def residentes_disponibles():
    return (Residente.query.filter_by(activo=True)
            .order_by(Residente.nombre).all())

def crear(*, nombre, email, password, rol, residente_id=None):
    nombre, err = validar_nombre(nombre, campo="nombre")
    if err:
        return None, err
    email, err = validar_email(email)
    if err:
        return None, err
    password, err = validar_password(password)
    if err:
        return None, err
    if rol not in ROLES_VALIDOS:
        return None, "Rol inválido."
    if rol == "residente" and not residente_id:
        return None, "Debes asociar un residente para el rol Residente."
    try:
        usuario = Usuario(
            nombre=nombre, email=email, rol=rol,
            residente_id=residente_id or None,
        )
        usuario.set_password(password)
        db.session.add(usuario)
        db.session.commit()
        return usuario, None
    except IntegrityError:
        db.session.rollback()
        return None, "El correo ya existe"

def eliminar(usuario_id):
    usuario = Usuario.query.get(usuario_id)
    if not usuario:
        return False, "Usuario no encontrado."
    if usuario.rol == "admin":
        return False, "No se puede eliminar un administrador."
    # Desvincular registros de auditoría (accesos/novedades quedan como histórico
    # sin usuario). Sin esto el DELETE falla por FK en Postgres/MySQL y el usuario
    # no se elimina.
    Acceso.query.filter_by(guardia_id=usuario_id).update({"guardia_id": None})
    Novedad.query.filter_by(guardia_id=usuario_id).update({"guardia_id": None})
    db.session.delete(usuario)
    db.session.commit()
    return True, None
