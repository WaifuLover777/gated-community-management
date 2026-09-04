"""Lógica de la garita inteligente: validación de QR (Fase 8)."""
import os
import uuid

from datetime import datetime, timedelta, date

from flask import current_app
from extensions import db
from models import (Visita, Residente, Autorizado, Vehiculo, Cuota, Acceso,
                    ListaNegra, RostroEnrolado)
from core.utils import PIN_TTL_HORAS
from core.validators import validar_placa
from modules.accesos import services as accesos_services
from core.reconocimiento import qr, rostros, color


def _resultado(ok, mensaje, **extra):
    base = {"ok": ok, "mensaje": mensaje}
    base.update(extra)
    return base


def validar_qr(contenido, guardia_id=None):
    """Valida el texto de un QR y registra el acceso. Devuelve un dict de resultado."""
    if not contenido:
        return _resultado(False, "QR vacío o ilegible.")

    if contenido.startswith(qr.PREFIJO_VISITA):
        return _validar_visita(contenido[len(qr.PREFIJO_VISITA):], guardia_id)
    if contenido.startswith(qr.PREFIJO_RESIDENTE):
        return _validar_residente(contenido[len(qr.PREFIJO_RESIDENTE):], guardia_id)
    if contenido.startswith(qr.PREFIJO_AUTORIZADO):
        return _validar_autorizado(contenido[len(qr.PREFIJO_AUTORIZADO):], guardia_id)
    return _resultado(False, "QR no reconocido por el sistema.")


def _validar_visita(token, guardia_id):
    visita = Visita.query.filter_by(token=token).first()
    if not visita:
        return _resultado(False, "Invitación no encontrada.")
    if visita.estado == "usado":
        return _resultado(False, "Esta invitación ya fue utilizada.")
    if visita.estado != "pendiente":
        return _resultado(False, f"Invitación en estado '{visita.estado}'.")
    limite = datetime.utcnow() - timedelta(hours=PIN_TTL_HORAS)
    if visita.fecha_creacion and visita.fecha_creacion < limite:
        visita.estado = "expirado"
        db.session.commit()
        return _resultado(False, "Invitación expirada.")

    visita.estado = "usado"
    visita.fecha_entrada = datetime.utcnow()
    db.session.commit()
    accesos_services.registrar(
        tipo="entrada", resultado="qr", placa=visita.placa_vehiculo,
        guardia_id=guardia_id, visita_id=visita.id,
        observacion=f"Ingreso por QR — visita {visita.nombre_visitante}",
    )
    return _resultado(True, f"Entrada autorizada: {visita.nombre_visitante}",
                      tipo="visita", visitante=visita.nombre_visitante,
                      casa=visita.casa.numero if visita.casa else None)


def _validar_residente(firma, guardia_id):
    rid = qr.verificar_residente(firma)
    if not rid:
        return _resultado(False, "Credencial de residente inválida.")
    residente = Residente.query.get(rid)
    if not residente or not residente.activo:
        return _resultado(False, "Residente no encontrado o inactivo.")
    accesos_services.registrar(
        tipo="entrada", resultado="qr", guardia_id=guardia_id,
        residente_id=residente.id,
        observacion=f"Ingreso por QR — residente {residente.nombre}",
    )
    return _resultado(True, f"Bienvenido, {residente.nombre}",
                      tipo="residente", residente=residente.nombre,
                      casa=residente.casa.numero if residente.casa else None)


def _validar_autorizado(token, guardia_id):
    a = Autorizado.query.filter_by(token=token).first()
    if not a:
        return _resultado(False, "Autorización no encontrada.")
    if not a.activo:
        return _resultado(False, "Autorización desactivada.")
    if a.residente and not a.residente.activo:
        return _resultado(False, "El residente que autorizó ya no está activo.")
    hoy = date.today()
    if a.vigencia_desde and hoy < a.vigencia_desde:
        return _resultado(False, "La autorización aún no está vigente.")
    if a.vigencia_hasta and hoy > a.vigencia_hasta:
        return _resultado(False, "La autorización está vencida.")
    accesos_services.registrar(
        tipo="entrada", resultado="qr", guardia_id=guardia_id,
        observacion=f"Ingreso por QR — autorizado {a.nombre} ({a.relacion or 'recurrente'})",
    )
    return _resultado(True, f"Acceso autorizado: {a.nombre}",
                      tipo="autorizado", persona=a.nombre,
                      casa=a.casa.numero if a.casa else None)



def en_lista_negra(placa):
    if not placa:
        return None
    return ListaNegra.query.filter_by(placa=placa, activo=True).first()

def vehiculo_dentro(placa):
    """True si el último acceso de la placa fue una entrada sin salida posterior."""
    if not placa:
        return False
    ultimo = (Acceso.query.filter(Acceso.placa == placa)
              .order_by(Acceso.fecha_hora.desc()).first())
    return bool(ultimo and ultimo.tipo == "entrada"
                and ultimo.resultado not in ("denegado",))

def _estado_financiero(casa_id):
    morosas = Cuota.query.filter(
        Cuota.casa_id == casa_id,
        Cuota.estado.in_(["pendiente", "vencido"]),
    ).count()
    return "al_dia" if morosas == 0 else "moroso"

def _guardar_evidencia(imagen_bytes):
    if not imagen_bytes:
        return None
    nombre = f"{uuid.uuid4().hex}.jpg"
    ruta = os.path.join(current_app.config["EVIDENCIA_DIR"], nombre)
    with open(ruta, "wb") as fh:
        fh.write(imagen_bytes)
    return nombre

def procesar_placas(*, placa_frontal, placa_trasera, tipo="entrada",
                    foto_bytes=None, guardia_id=None):
    pf, _ = validar_placa(placa_frontal, requerido=False)
    pt, _ = validar_placa(placa_trasera, requerido=False)
    placa = pf or pt
    if not placa:
        col = color.color_dominante(foto_bytes)
        extra = f" Vehículo color {col}." if col else ""
        return _resultado(False, f"No se pudo leer ninguna placa.{extra}", color=col)

    obs = []
    if pf and pt and pf != pt:
        obs.append(f"⚠️ Discrepancia frontal({pf}) / trasera({pt}) — revisar")

    foto = _guardar_evidencia(foto_bytes)

    veto = en_lista_negra(placa)
    if veto:
        accesos_services.registrar(
            tipo=tipo, resultado="denegado", metodo="placa", placa=placa,
            placa_frontal=pf, placa_trasera=pt, foto_evidencia=foto, guardia_id=guardia_id,
            observacion="; ".join(obs + [f"LISTA NEGRA: {veto.motivo or 'sin motivo'}"]),
        )
        return _resultado(False, f"🚨 Placa {placa} en lista negra. Acceso denegado.",
                          alerta=True, placa=placa)

    if tipo == "entrada" and vehiculo_dentro(placa):
        accesos_services.registrar(
            tipo=tipo, resultado="denegado", metodo="placa", placa=placa,
            placa_frontal=pf, placa_trasera=pt, foto_evidencia=foto, guardia_id=guardia_id,
            observacion="; ".join(obs + ["Anti-passback: el vehículo ya figura dentro"]),
        )
        return _resultado(False, f"El vehículo {placa} ya está registrado dentro.",
                          placa=placa)

    vehiculo = (Vehiculo.query.filter_by(placa=placa).join(Residente)
                .filter(Residente.activo.is_(True)).first())
    if vehiculo:
        residente = vehiculo.residente
        estado = _estado_financiero(residente.casa_id)
        autorizado = (estado == "al_dia") or tipo == "salida"
        resultado = "autorizado" if autorizado else "denegado"
        if estado == "moroso":
            obs.append("Casa con cuotas pendientes")
        acc = accesos_services.registrar(
            tipo=tipo, resultado=resultado, metodo="placa", placa=placa,
            placa_frontal=pf, placa_trasera=pt, foto_evidencia=foto,
            guardia_id=guardia_id, residente_id=residente.id, confianza=0.99,
            observacion="; ".join(obs) or f"Vehículo de {residente.nombre}",
        )
        msg = f"{'Salida' if tipo=='salida' else 'Entrada'} de {residente.nombre} (Casa {residente.casa.numero})"
        if not autorizado:
            msg += " — DENEGADO: cuotas pendientes"
        return _resultado(autorizado, msg, placa=placa, residente=residente.nombre,
                          estado_financiero=estado, discrepancia=bool(pf and pt and pf != pt))

    col = color.color_dominante(foto_bytes)
    if col:
        obs.append(f"Vehículo color {col}")
    accesos_services.registrar(
        tipo=tipo, resultado="manual", metodo="placa", placa=placa,
        placa_frontal=pf, placa_trasera=pt, foto_evidencia=foto, guardia_id=guardia_id,
        observacion="; ".join(obs + ["Placa no registrada — verificar manualmente"]),
    )
    return _resultado(False,
                      f"Placa {placa} no registrada{f' (color {col})' if col else ''}. "
                      "Verificación manual del guardia.",
                      placa=placa, desconocida=True, color=col,
                      discrepancia=bool(pf and pt and pf != pt))


def listar_lista_negra():
    return ListaNegra.query.order_by(ListaNegra.activo.desc(), ListaNegra.placa).all()

def agregar_lista_negra(placa, motivo):
    placa, err = validar_placa(placa, requerido=True)
    if err:
        return err
    existente = ListaNegra.query.filter_by(placa=placa).first()
    if existente:
        existente.activo = True
        existente.motivo = (motivo or "").strip()[:200]
    else:
        db.session.add(ListaNegra(placa=placa, motivo=(motivo or "").strip()[:200], activo=True))
    db.session.commit()
    return None

def alternar_lista_negra(entry_id):
    e = ListaNegra.query.get(entry_id)
    if e:
        e.activo = not e.activo
        db.session.commit()



def enrolar_rostro(imagen_bytes, residente_id, *, consentimiento=False):
    """Calcula y guarda el embedding facial de un residente. Requiere consentimiento."""
    if not consentimiento:
        return "Debes aceptar el consentimiento de uso de datos biométricos."
    embs = rostros.extraer_embeddings(imagen_bytes)
    if not embs:
        return "No se detectó un rostro en la imagen. Intenta con otra foto."
    foto = _guardar_evidencia(imagen_bytes)
    existente = RostroEnrolado.query.filter_by(residente_id=residente_id,
                                               tipo="residente").first()
    if existente:
        existente.embedding = rostros.serializar(embs[0])
        existente.foto = foto
        existente.consentimiento = True
    else:
        db.session.add(RostroEnrolado(
            tipo="residente", residente_id=residente_id,
            embedding=rostros.serializar(embs[0]), foto=foto, consentimiento=True))
    db.session.commit()
    return None

def _enrolados_residentes():
    # Solo residentes activos: un dado de baja no debe seguir siendo reconocido.
    rows = (RostroEnrolado.query.join(Residente, RostroEnrolado.residente_id == Residente.id)
            .filter(RostroEnrolado.tipo == "residente", Residente.activo.is_(True)).all())
    return rows, [rostros.deserializar(r.embedding) for r in rows]

def procesar_rostros(imagen_bytes, *, guardia_id=None):
    """Identifica los ocupantes (multi-rostro) contra residentes enrolados."""
    embs = rostros.extraer_embeddings(imagen_bytes)
    if not embs:
        return _resultado(False, "No se detectaron rostros en la imagen.")
    umbral = current_app.config.get("RECOG_ROSTRO_UMBRAL", 0.45)
    rows, candidatos = _enrolados_residentes()

    ocupantes, identificados, desconocidos = [], [], 0
    for emb in embs:
        idx, score = rostros.comparar(emb, candidatos)
        if idx >= 0 and score >= umbral:
            res = rows[idx].residente
            nombre = res.nombre if res else "Residente"
            ocupantes.append({"nombre": nombre, "score": round(score, 3)})
            if res:
                identificados.append(res)
        else:
            desconocidos += 1
            ocupantes.append({"nombre": "Desconocido", "score": round(score, 3)})

    foto = _guardar_evidencia(imagen_bytes)
    detalle = ", ".join(f"{o['nombre']}({o['score']})" for o in ocupantes)
    resultado = "autorizado" if identificados else "manual"
    accesos_services.registrar(
        tipo="entrada", resultado=resultado, metodo="rostro", foto_evidencia=foto,
        guardia_id=guardia_id,
        residente_id=identificados[0].id if identificados else None,
        confianza=max((o["score"] for o in ocupantes), default=0.0),
        observacion=f"Ocupantes: {len(ocupantes)} — {detalle}"
                    + (f" — {desconocidos} desconocido(s)" if desconocidos else ""),
    )
    ok = bool(identificados)
    msg = (f"Identificado: {identificados[0].nombre}" if ok
           else "Rostro(s) no identificado(s) — verificación manual")
    return _resultado(ok, msg, ocupantes=ocupantes, total=len(ocupantes),
                      desconocidos=desconocidos, alerta=(desconocidos > 0))


def purgar_evidencia(dias=None):
    """Borra fotos de evidencia y embedding antiguos según política de retención."""
    dias = dias if dias is not None else current_app.config.get("EVIDENCIA_RETENCION_DIAS", 30)
    limite = datetime.utcnow() - timedelta(days=dias)
    borrados = 0
    carpeta = current_app.config["EVIDENCIA_DIR"]
    for acc in Acceso.query.filter(Acceso.foto_evidencia.isnot(None),
                                   Acceso.fecha_hora < limite).all():
        ruta = os.path.join(carpeta, acc.foto_evidencia)
        if os.path.exists(ruta):
            os.remove(ruta)
        acc.foto_evidencia = None
        borrados += 1
    db.session.commit()
    return borrados
