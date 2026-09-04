from datetime import date
from flask import current_app
from sqlalchemy import func, or_, and_
from extensions import db
from models import Casa, Cuota
from core.utils import filtro_casa_cond

ESTADOS = ("pendiente", "en_revision", "pagado", "vencido")

def _tasa_mora():
    try:
        return float(current_app.config.get("RECARGO_MORA_MENSUAL", 0.10))
    except RuntimeError:
        return 0.10

def meses_atraso(cuota, hoy=None):
    hoy = hoy or date.today()
    n = (hoy.year - cuota.anio) * 12 + (hoy.month - cuota.mes)
    return n if n > 0 else 0

def calcular_recargo(cuota, hoy=None):
    if cuota.estado in ("pagado", "en_revision"):
        return round(cuota.recargo or 0, 2)
    return round((cuota.monto or 0) * _tasa_mora() * meses_atraso(cuota, hoy), 2)

def total_con_recargo(cuota, hoy=None):
    return round((cuota.monto or 0) + calcular_recargo(cuota, hoy), 2)

def marcar_vencidas_auto():
    hoy = date.today()
    cuotas = Cuota.query.filter(
        Cuota.estado == "pendiente",
        or_(Cuota.anio < hoy.year,
            and_(Cuota.anio == hoy.year, Cuota.mes < hoy.month)),
    ).all()
    for cu in cuotas:
        cu.estado = "vencido"
    if cuotas:
        db.session.commit()
    return len(cuotas)

def listar_cuotas(anio=None, mes=None, estado=None, casa=None):
    marcar_vencidas_auto()
    q = Cuota.query.join(Casa)
    if anio:
        q = q.filter(Cuota.anio == anio)
    if mes:
        q = q.filter(Cuota.mes == mes)
    if estado:
        q = q.filter(Cuota.estado == estado)
    if casa and casa.strip():
        q = q.filter(filtro_casa_cond(casa))
    cuotas = q.order_by(Cuota.anio.desc(), Casa.manzana, Casa.numero, Cuota.mes).all()
    for cu in cuotas:
        cu.casa_numero = cu.casa.numero
        cu.manzana = cu.casa.manzana
        cu.recargo_calc = calcular_recargo(cu)
        cu.total = total_con_recargo(cu)
    return cuotas

def totales(anio=None):
    marcar_vencidas_auto()
    q = db.session.query(Cuota.estado, func.coalesce(func.sum(Cuota.monto), 0))
    if anio:
        q = q.filter(Cuota.anio == anio)
    rows = q.group_by(Cuota.estado).all()
    d = {"cobrado": 0, "pendiente": 0, "vencido": 0, "en_revision": 0}
    for estado, total in rows:
        if estado == "pagado":
            d["cobrado"] = total
        elif estado == "pendiente":
            d["pendiente"] = total
        elif estado == "vencido":
            d["vencido"] = total
        elif estado == "en_revision":
            d["en_revision"] = total
    return d

def generar(mes, anio):
    if not (1 <= mes <= 12):
        return 0, "Mes inválido."
    hoy = date.today()
    if anio < hoy.year or (anio == hoy.year and mes < hoy.month):
        return 0, ("No puedes generar cuotas de meses o años pasados. "
                   "Solo el mes actual en adelante.")
    generadas = 0
    for casa in Casa.query.all():
        existe = Cuota.query.filter_by(casa_id=casa.id, mes=mes, anio=anio,
                                       concepto="").first()
        if not existe:
            db.session.add(Cuota(casa_id=casa.id, mes=mes, anio=anio,
                                 monto=casa.alicuota, estado="pendiente",
                                 tipo="ordinaria", concepto=""))
            generadas += 1
    db.session.commit()
    return generadas, None

def generar_extraordinaria(*, concepto, monto, anio, mes, casa_id=None):
    concepto = (concepto or "").strip()
    if not concepto:
        return 0, "El concepto es obligatorio."
    if len(concepto) > 80:
        return 0, "El concepto no puede superar 80 caracteres."
    try:
        monto = float(monto)
    except (TypeError, ValueError):
        return 0, "Monto inválido."
    if monto <= 0:
        return 0, "El monto debe ser mayor que cero."
    if not (1 <= mes <= 12):
        return 0, "Mes inválido."
    hoy = date.today()
    if anio < hoy.year or (anio == hoy.year and mes < hoy.month):
        return 0, ("No puedes generar cobros de meses o años pasados. "
                   "Solo el mes actual en adelante.")
    if casa_id:
        casas = Casa.query.filter_by(id=casa_id).all()
        if not casas:
            return 0, "Casa no encontrada."
    else:
        casas = Casa.query.all()
    generadas = 0
    for casa in casas:
        existe = Cuota.query.filter_by(casa_id=casa.id, mes=mes, anio=anio,
                                       concepto=concepto).first()
        if existe:
            continue
        db.session.add(Cuota(casa_id=casa.id, mes=mes, anio=anio, monto=monto,
                             tipo="extraordinaria", concepto=concepto,
                             estado="pendiente"))
        generadas += 1
    db.session.commit()
    return generadas, None

def reporte_cobranza(anio, mes=None):
    marcar_vencidas_auto()
    q = Cuota.query.join(Casa)
    if anio:
        q = q.filter(Cuota.anio == anio)
    if mes:
        q = q.filter(Cuota.mes == mes)
    cuotas = q.all()

    esperado = cobrado = recargo_cobrado = pendiente = vencido = en_revision = 0.0
    morosos = {}
    for cu in cuotas:
        monto = cu.monto or 0
        esperado += monto
        if cu.estado == "pagado":
            cobrado += monto
            recargo_cobrado += cu.recargo or 0
        elif cu.estado == "en_revision":
            en_revision += monto
        elif cu.estado == "pendiente":
            pendiente += monto
        elif cu.estado == "vencido":
            vencido += monto
            rec = calcular_recargo(cu)
            m = morosos.setdefault(cu.casa_id, {
                "casa": f"{cu.casa.manzana}-{cu.casa.numero}",
                "cuotas_vencidas": 0, "max_atraso": 0, "total_adeudado": 0.0,
            })
            m["cuotas_vencidas"] += 1
            m["max_atraso"] = max(m["max_atraso"], meses_atraso(cu))
            m["total_adeudado"] += monto + rec

    porcentaje = round((cobrado / esperado) * 100, 1) if esperado else 0.0
    morosos_list = sorted(morosos.values(),
                          key=lambda x: x["total_adeudado"], reverse=True)
    for m in morosos_list:
        m["total_adeudado"] = round(m["total_adeudado"], 2)
    return {
        "esperado": round(esperado, 2),
        "cobrado": round(cobrado, 2),
        "recargo_cobrado": round(recargo_cobrado, 2),
        "recaudado_total": round(cobrado + recargo_cobrado, 2),
        "pendiente": round(pendiente, 2),
        "vencido": round(vencido, 2),
        "en_revision": round(en_revision, 2),
        "porcentaje_recaudacion": porcentaje,
        "morosos": morosos_list,
    }

def anios_disponibles():
    rows = db.session.query(Cuota.anio).distinct().order_by(Cuota.anio.desc()).all()
    return [r[0] for r in rows]

def obtener_cuota(cuota_id):
    cu = Cuota.query.get(cuota_id)
    if cu:
        cu.casa_numero = cu.casa.numero
    return cu

def confirmar_transferencia(cuota_id):
    cu = Cuota.query.get(cuota_id)
    if not cu:
        return None, "Cuota no encontrada"
    if cu.estado != "en_revision":
        return None, "Esta cuota no está en revisión"
    cu.estado = "pagado"
    cu.fecha_pago = str(date.today())
    db.session.commit()
    return cu, None

def rechazar_transferencia(cuota_id):
    cu = Cuota.query.get(cuota_id)
    if not cu:
        return None, "Cuota no encontrada"
    if cu.estado != "en_revision":
        return None, "Esta cuota no está en revisión"
    cu.estado = "pendiente"
    cu.comprobante = None
    cu.metodo_pago = None
    cu.recargo = 0
    db.session.commit()
    return cu, None
