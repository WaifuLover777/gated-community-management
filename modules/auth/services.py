from sqlalchemy.exc import IntegrityError
from extensions import db
from models import Usuario, Residente, Casa
from core.validators import (validar_nombre, validar_cedula, validar_telefono,
                             validar_email)

def autenticar(email, password):
    usuario = Usuario.query.filter_by(email=email).first()
    if usuario and usuario.check_password(password):
        if usuario.residente and not usuario.residente.activo:
            return None  # residente dado de baja: sin acceso
        return usuario
    return None

def casa_por_pin(pin):
    pin = (pin or "").strip()
    if not pin:
        return None
    return Casa.query.filter_by(pin_registro=pin).first()

def registrar_residente(*, nombre, cedula, telefono, email, password, pin, tipo):
    casa = casa_por_pin(pin)
    if not casa:
        return None, "PIN inválido o ya utilizado."
    nombre, err = validar_nombre(nombre, campo="nombre")
    if err:
        return None, err
    cedula, err = validar_cedula(cedula)
    if err:
        return None, err
    telefono, err = validar_telefono(telefono, requerido=False)
    if err:
        return None, err
    email, err = validar_email(email)
    if err:
        return None, err
    if tipo not in ("propietario", "inquilino"):
        return None, "Tipo de residente inválido."

    if casa.capacidad:
        activos = Residente.query.filter_by(casa_id=casa.id, activo=True).count()
        if activos >= casa.capacidad:
            return None, "La villa ya alcanzó su capacidad máxima de residentes."
    try:
        residente = Residente(
            casa_id=casa.id, nombre=nombre, cedula=cedula,
            telefono=telefono, email=email, tipo=tipo,
        )
        db.session.add(residente)
        db.session.flush()

        usuario = Usuario(
            nombre=nombre, email=email, rol="residente",
            residente_id=residente.id,
        )
        usuario.set_password(password)
        db.session.add(usuario)
        casa.pin_registro = None
        db.session.commit()
        return usuario, None
    except IntegrityError:
        db.session.rollback()
        return None, "El correo o la cédula ya están registrados"
    except Exception as e:
        db.session.rollback()
        return None, f"Error al registrar: {e}"
