from datetime import date, datetime
from sqlalchemy.exc import IntegrityError
from extensions import db
from models import Residente, Cuota, Vehiculo, Comunicado, Visita
from core.validators import validar_datos_visita
from core.utils import guardar_imagen

def datos_residente(residente_id):
    r = Residente.query.get(residente_id)
    if r and r.casa:
        r.casa_numero = r.casa.numero
        r.manzana = r.casa.manzana
    return r

def resumen_cuotas(casa_id):
    from modules.pagos.services import marcar_vencidas_auto
    marcar_vencidas_auto()
    pendientes = Cuota.query.filter_by(casa_id=casa_id, estado="pendiente").count()
    vencidas = Cuota.query.filter_by(casa_id=casa_id, estado="vencido").count()
    return pendientes, vencidas

def comunicados_activos(limite=None):
    q = (Comunicado.query
         .filter(Comunicado.activo.is_(True),
                 Comunicado.fecha_publicacion <= datetime.utcnow())
         .order_by(Comunicado.fecha_publicacion.desc()))
    return q.limit(limite).all() if limite else q.all()

def cuotas_de_casa(casa_id):
    from modules.pagos.services import (calcular_recargo, total_con_recargo,
                                         marcar_vencidas_auto)
    marcar_vencidas_auto()
    cuotas = (Cuota.query.filter_by(casa_id=casa_id)
              .order_by(Cuota.anio.desc(), Cuota.mes.desc()).all())
    for cu in cuotas:
        cu.recargo_calc = calcular_recargo(cu)
        cu.total = total_con_recargo(cu)
    return cuotas

def deuda_de_casa(casa_id):
    from modules.pagos.services import calcular_recargo, marcar_vencidas_auto
    from modules.multas.services import total_pendiente_casa
    marcar_vencidas_auto()
    cuotas = Cuota.query.filter(
        Cuota.casa_id == casa_id,
        Cuota.estado.in_(("pendiente", "vencido")),
    ).all()
    pendiente = vencido = recargo = 0.0
    for cu in cuotas:
        monto = cu.monto or 0
        if cu.estado == "vencido":
            vencido += monto
            recargo += calcular_recargo(cu)
        else:
            pendiente += monto
    multas_total, multas_num = total_pendiente_casa(casa_id)
    total = pendiente + vencido + recargo + multas_total
    return {
        "pendiente": round(pendiente, 2),
        "vencido": round(vencido, 2),
        "recargo": round(recargo, 2),
        "multas": round(multas_total, 2),
        "num_multas": multas_num,
        "total": round(total, 2),
        "num_cuotas": len(cuotas),
    }

def vehiculos_de(residente_id):
    return Vehiculo.query.filter_by(residente_id=residente_id).all()

def obtener_vehiculo_de(vehiculo_id, residente_id):
    return Vehiculo.query.filter_by(id=vehiculo_id, residente_id=residente_id).first()

def crear_vehiculo_residente(residente_id, *, placa, marca, modelo, color):
    from modules.residentes.services import crear_vehiculo
    return crear_vehiculo(residente_id=residente_id, placa=placa, marca=marca,
                          modelo=modelo, color=color)

def editar_vehiculo(vehiculo_id, residente_id, *, placa, marca, modelo, color):
    from core.validators import validar_placa, limpiar_texto
    v = obtener_vehiculo_de(vehiculo_id, residente_id)
    if not v:
        return "Vehículo no encontrado"
    placa, err = validar_placa(placa)
    if err:
        return err
    marca, _ = limpiar_texto(marca, campo="marca", maximo=40)
    modelo, _ = limpiar_texto(modelo, campo="modelo", maximo=10)
    color, _ = limpiar_texto(color, campo="color", maximo=30)
    try:
        v.placa, v.marca, v.modelo, v.color = placa, marca, modelo, color
        db.session.commit()
        return None
    except IntegrityError:
        db.session.rollback()
        return f"Ya existe un vehículo con la placa '{placa}'"

def eliminar_vehiculo(vehiculo_id, residente_id):
    v = obtener_vehiculo_de(vehiculo_id, residente_id)
    if not v:
        return "Vehículo no encontrado"
    db.session.delete(v)
    db.session.commit()
    return None

def visitas_de_casa(casa_id):
    return (Visita.query.filter_by(casa_id=casa_id)
            .order_by(Visita.fecha_creacion.desc()).limit(50).all())

def solicitar_visita(*, casa_id, nombre_visitante, cedula_visitante, motivo,
                     placa_vehiculo, autorizado_por):
    from core.utils import generar_pin, generar_token
    datos, err = validar_datos_visita(nombre_visitante, cedula_visitante,
                                      placa_vehiculo, motivo)
    if err:
        return err
    db.session.add(Visita(
        casa_id=casa_id, autorizado_por=autorizado_por, estado="pendiente",
        fecha_creacion=datetime.utcnow(), pin=generar_pin(),
        token=generar_token(), **datos,
    ))
    db.session.commit()
    return None

def actualizar_personas(casa_id, personas):
    from models import Casa
    casa = Casa.query.get(casa_id)
    if casa:
        casa.personas = int(personas) if personas else None
        db.session.commit()

def obtener_cuota_de_casa(cuota_id, casa_id):
    return Cuota.query.filter_by(id=cuota_id, casa_id=casa_id).first()

def pagar_cuota(cuota_id, casa_id, metodo_pago, upload_folder, archivo=None):
    cu = obtener_cuota_de_casa(cuota_id, casa_id)
    if not cu:
        return None, "Cuota no encontrada"
    if cu.estado == "pagado":
        return None, "Esta cuota ya está pagada"
    if cu.estado == "en_revision":
        return None, "Esta cuota ya tiene una transferencia en revisión"
    if metodo_pago not in ("online", "transferencia"):
        return None, "Método de pago inválido"

    from modules.pagos.services import calcular_recargo
    cu.recargo = calcular_recargo(cu)

    if metodo_pago == "transferencia":
        nombre_archivo, err = guardar_imagen(
            archivo, upload_folder, permitidas={"pdf", "jpg", "jpeg", "png"})
        if err:
            return None, "Formato no permitido. Sube PDF, JPG o PNG"
        if not nombre_archivo:
            return None, "Debes subir el comprobante de transferencia"
        cu.comprobante = nombre_archivo
        cu.metodo_pago = "transferencia"
        cu.estado = "en_revision"
    else:
        cu.metodo_pago = "online"
        cu.estado = "pagado"
        cu.fecha_pago = str(date.today())

    db.session.commit()
    return cu, None

def pagar_multa(multa_id, casa_id):
    from models import Multa
    m = Multa.query.filter_by(id=multa_id, casa_id=casa_id).first()
    if not m:
        return None, "Multa no encontrada"
    if m.estado != "pendiente":
        return None, "Esta multa no está pendiente de pago"
    m.estado = "pagada"
    m.fecha_pago = str(date.today())
    db.session.commit()
    return m, None
