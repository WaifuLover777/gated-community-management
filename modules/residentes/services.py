from datetime import date
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from extensions import db
from models import Casa, Residente, Vehiculo, RostroEnrolado
from core.utils import generar_pin, filtro_casa_cond
from core.validators import (validar_nombre, validar_cedula, validar_telefono,
                             validar_email, validar_placa, validar_entero,
                             limpiar_texto)

def listar_casas():
    casas = Casa.query.order_by(Casa.manzana, Casa.numero).all()
    for c in casas:
        c.num_residentes = Residente.query.filter_by(casa_id=c.id, activo=True).count()
    return casas

def obtener_casa(casa_id):
    return Casa.query.get(casa_id)

def casas_select():
    return Casa.query.order_by(Casa.manzana, Casa.numero).all()

def generar_pin_casa(casa_id):
    casa = Casa.query.get(casa_id)
    if not casa:
        return None, "Casa no encontrada."

    for _ in range(20):
        pin = generar_pin()
        choque = Casa.query.filter(Casa.pin_registro == pin,
                                   Casa.id != casa.id).first()
        if not choque:
            casa.pin_registro = pin
            db.session.commit()
            return pin, None
    return None, "No se pudo generar un PIN único, inténtalo de nuevo."

def _validar_casa(numero, capacidad, personas):
    numero, err = limpiar_texto(numero, campo="número de casa", maximo=20, requerido=True)
    if err:
        return None, None, None, err
    capacidad, err = validar_entero(capacidad, campo="capacidad", minimo=1, maximo=50,
                                    requerido=False)
    if err:
        return None, None, None, err
    personas, err = validar_entero(personas, campo="personas", minimo=0, maximo=50,
                                   requerido=False)
    if err:
        return None, None, None, err
    return numero, capacidad, personas, None

def crear_casa(*, numero, manzana, area_m2, alicuota, estado, tipo=None, color=None,
               capacidad=None, personas=None):
    numero, capacidad, personas, err = _validar_casa(numero, capacidad, personas)
    if err:
        return err
    try:
        db.session.add(Casa(
            numero=numero, manzana=(manzana or "").strip(),
            tipo=(tipo or "").strip() or None, color=(color or "").strip() or None,
            area_m2=area_m2 or 0, alicuota=alicuota or 0, estado=estado or "ocupada",
            capacidad=capacidad, personas=personas,
        ))
        db.session.commit()
        return None
    except IntegrityError:
        db.session.rollback()
        return f"Ya existe una casa con el número '{numero}'"

def actualizar_casa(casa_id, *, numero, manzana, area_m2, alicuota, estado, tipo=None,
                    color=None, capacidad=None, personas=None):
    c = Casa.query.get(casa_id)
    if not c:
        return
    numero, capacidad, personas, err = _validar_casa(numero, capacidad, personas)
    if err:
        return err
    try:
        c.numero, c.manzana = numero, (manzana or "").strip()
        c.tipo = (tipo or "").strip() or None
        c.color = (color or "").strip() or None
        c.area_m2, c.alicuota, c.estado = area_m2 or 0, alicuota or 0, estado or "ocupada"
        c.capacidad = capacidad
        c.personas = personas
        db.session.commit()
        return None
    except IntegrityError:
        db.session.rollback()
        return f"Ya existe una casa con el número '{numero}'"

def _anexar_casa(residente):
    if residente.casa:
        residente.casa_numero = residente.casa.numero
        residente.manzana = residente.casa.manzana
    return residente

def listar_residentes(filtro=""):
    q = Residente.query.join(Casa).filter(Residente.activo.is_(True))
    if filtro:
        like = f"%{filtro}%"
        q = q.filter(or_(Residente.nombre.like(like),
                         Residente.cedula.like(like),
                         filtro_casa_cond(filtro)))
    residentes = q.order_by(Casa.manzana, Casa.numero, Residente.nombre).all()
    return [_anexar_casa(r) for r in residentes]

def obtener_residente(residente_id):
    return Residente.query.get(residente_id)

def _validar_residente(nombre, cedula, telefono, email, tipo):
    nombre, err = validar_nombre(nombre, campo="nombre")
    if err:
        return None, err
    cedula, err = validar_cedula(cedula)
    if err:
        return None, err
    telefono, err = validar_telefono(telefono, requerido=False)
    if err:
        return None, err
    email, err = validar_email(email, requerido=False)
    if err:
        return None, err
    if tipo not in ("propietario", "inquilino"):
        return None, "Tipo de residente inválido."
    return {"nombre": nombre, "cedula": cedula, "telefono": telefono,
            "email": email, "tipo": tipo}, None

def crear_residente(*, casa_id, nombre, cedula, telefono, email, tipo, fecha_ingreso=None):
    datos, err = _validar_residente(nombre, cedula, telefono, email, tipo)
    if err:
        return err
    if datos["tipo"] == "propietario":
        choque = Residente.query.filter_by(casa_id=casa_id, tipo="propietario", activo=True).first()
        if choque:
            return "Esta villa ya tiene un propietario activo."
    fi = None
    if fecha_ingreso:
        try:
            fi = date.fromisoformat(fecha_ingreso)
        except ValueError:
            fi = None
    try:
        db.session.add(Residente(casa_id=casa_id, fecha_ingreso=fi or date.today(), **datos))
        db.session.commit()
        return None
    except IntegrityError:
        db.session.rollback()
        return f"Ya existe un residente con la cédula '{datos['cedula']}'"

def actualizar_residente(residente_id, *, casa_id, nombre, cedula, telefono, email, tipo):
    r = Residente.query.get(residente_id)
    if not r:
        return "Residente no encontrado."
    datos, err = _validar_residente(nombre, cedula, telefono, email, tipo)
    if err:
        return err
    try:
        r.casa_id = casa_id
        for k, v in datos.items():
            setattr(r, k, v)
        db.session.commit()
        return None
    except IntegrityError:
        db.session.rollback()
        return f"Ya existe un residente con la cédula '{datos['cedula']}'"

def dar_de_baja(residente_id):
    r = Residente.query.get(residente_id)
    if r:
        r.activo = False
        # Borrar el biométrico: no conservar el rostro de alguien dado de baja.
        RostroEnrolado.query.filter_by(residente_id=residente_id).delete()
        db.session.commit()

def listar_vehiculos():
    vehiculos = (Vehiculo.query.join(Residente).join(Casa)
                 .filter(Residente.activo.is_(True))
                 .order_by(Casa.numero, Residente.nombre).all())
    for v in vehiculos:
        v.residente_nombre = v.residente.nombre
        v.casa_numero = v.residente.casa.numero
    return vehiculos

def residentes_para_select():
    residentes = (Residente.query.join(Casa).filter(Residente.activo.is_(True))
                  .order_by(Casa.numero, Residente.nombre).all())
    for r in residentes:
        r.numero = r.casa.numero
    return residentes

def crear_vehiculo(*, residente_id, placa, marca, modelo, color):
    placa, err = validar_placa(placa)
    if err:
        return err
    marca, _ = limpiar_texto(marca, campo="marca", maximo=40)
    modelo, _ = limpiar_texto(modelo, campo="modelo", maximo=10)
    color, _ = limpiar_texto(color, campo="color", maximo=30)
    try:
        db.session.add(Vehiculo(residente_id=residente_id, placa=placa,
                                marca=marca, modelo=modelo, color=color))
        db.session.commit()
        return None
    except IntegrityError:
        db.session.rollback()
        return f"Ya existe un vehículo con la placa '{placa}'"
