from flask import (Blueprint, render_template, request, redirect, url_for,
                   session, flash, current_app, Response, abort)
from core.decorators import residente_required
from core.utils import MESES
from modules.portal import services

portal_bp = Blueprint("portal", __name__)

_SERVICE_WORKER = """
const CACHE = 'villa-ceibos-v1';
const SHELL = ['/portal', '/static/css/main.css', '/static/icons/icon-192.png'];
self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(SHELL)).then(() => self.skipWaiting()));
});
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(ks =>
    Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k)))
  ).then(() => self.clients.claim()));
});
self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET') return;
  e.respondWith(
    fetch(e.request).then(res => {
      const copy = res.clone();
      caches.open(CACHE).then(c => c.put(e.request, copy));
      return res;
    }).catch(() => caches.match(e.request).then(r => r || caches.match('/portal')))
  );
});
"""

@portal_bp.route("/sw.js")
def service_worker():
    return current_app.response_class(_SERVICE_WORKER, mimetype="application/javascript")

@portal_bp.route("/portal")
@residente_required
def inicio():
    residente = services.datos_residente(session["residente_id"])
    pendientes, vencidas = services.resumen_cuotas(residente.casa_id)
    return render_template("portal/inicio.html", residente=residente,
                           cuotas_pendientes=pendientes, cuotas_vencidas=vencidas,
                           deuda=services.deuda_de_casa(residente.casa_id),
                           comunicados=services.comunicados_activos(limite=3))

@portal_bp.route("/portal/cuotas")
@residente_required
def cuotas():
    from modules.multas.services import multas_de_casa
    residente = services.datos_residente(session["residente_id"])
    return render_template("portal/cuotas.html",
                           cuotas=services.cuotas_de_casa(residente.casa_id),
                           deuda=services.deuda_de_casa(residente.casa_id),
                           multas=multas_de_casa(residente.casa_id),
                           residente=residente, meses=MESES)

@portal_bp.route("/portal/vehiculos")
@residente_required
def vehiculos():
    return render_template("portal/vehiculos.html",
                           vehiculos=services.vehiculos_de(session["residente_id"]))

@portal_bp.route("/portal/vehiculos/nuevo", methods=["GET", "POST"])
@residente_required
def nuevo_vehiculo():
    if request.method == "POST":
        err = services.crear_vehiculo_residente(
            session["residente_id"],
            placa=request.form.get("placa", ""),
            marca=request.form.get("marca", ""),
            modelo=request.form.get("modelo", ""),
            color=request.form.get("color", ""),
        )
        if err:
            flash(err, "error")
            return render_template("portal/vehiculo_form.html", vehiculo=None)
        flash("Vehículo registrado correctamente", "success")
        return redirect(url_for("portal.vehiculos"))
    return render_template("portal/vehiculo_form.html", vehiculo=None)

@portal_bp.route("/portal/vehiculos/<int:id>/editar", methods=["GET", "POST"])
@residente_required
def editar_vehiculo(id):
    vehiculo = services.obtener_vehiculo_de(id, session["residente_id"])
    if not vehiculo:
        flash("Vehículo no encontrado", "error")
        return redirect(url_for("portal.vehiculos"))
    if request.method == "POST":
        err = services.editar_vehiculo(
            id, session["residente_id"],
            placa=request.form.get("placa", ""),
            marca=request.form.get("marca", ""),
            modelo=request.form.get("modelo", ""),
            color=request.form.get("color", ""),
        )
        if err:
            flash(err, "error")
            return render_template("portal/vehiculo_form.html", vehiculo=vehiculo)
        flash("Vehículo actualizado", "success")
        return redirect(url_for("portal.vehiculos"))
    return render_template("portal/vehiculo_form.html", vehiculo=vehiculo)

@portal_bp.route("/portal/vehiculos/<int:id>/eliminar", methods=["POST"])
@residente_required
def eliminar_vehiculo(id):
    err = services.eliminar_vehiculo(id, session["residente_id"])
    flash(err or "Vehículo eliminado", "error" if err else "success")
    return redirect(url_for("portal.vehiculos"))

@portal_bp.route("/portal/comunicados")
@residente_required
def comunicados():
    return render_template("portal/comunicados.html",
                           comunicados=services.comunicados_activos())

@portal_bp.route("/portal/notificaciones")
@residente_required
def notificaciones():
    from core import notificaciones as notif
    rid = session["residente_id"]
    items = notif.bandeja(rid)
    notif.marcar_leidas(rid)
    return render_template("portal/notificaciones.html", notificaciones=items)

@portal_bp.route("/portal/visitas")
@residente_required
def visitas():
    residente = services.datos_residente(session["residente_id"])
    return render_template("portal/visitas.html",
                           visitas=services.visitas_de_casa(residente.casa_id))

@portal_bp.route("/portal/qr")
@residente_required
def qr_residente():
    from core.reconocimiento import qr
    return Response(qr.png_residente(session["residente_id"]), mimetype="image/png")

@portal_bp.route("/portal/rostro", methods=["GET", "POST"])
@residente_required
def enrolar_rostro():
    from modules.garita import services as garita_services
    from models import RostroEnrolado
    rid = session["residente_id"]
    if request.method == "POST":
        archivo = request.files.get("foto")
        consentimiento = request.form.get("consentimiento") == "on"
        if not archivo or not archivo.filename:
            flash("Sube una foto de tu rostro", "error")
        else:
            err = garita_services.enrolar_rostro(archivo.read(), rid,
                                                 consentimiento=consentimiento)
            flash(err or "Rostro enrolado correctamente", "error" if err else "success")
        return redirect(url_for("portal.enrolar_rostro"))
    enrolado = RostroEnrolado.query.filter_by(residente_id=rid, tipo="residente").first()
    return render_template("portal/rostro.html", enrolado=enrolado)

@portal_bp.route("/portal/visitas/<int:id>/qr")
@residente_required
def qr_visita(id):
    from core.reconocimiento import qr
    from models import Visita
    residente = services.datos_residente(session["residente_id"])
    v = Visita.query.filter_by(id=id, casa_id=residente.casa_id).first()
    if not v or not v.token:
        abort(404)
    return Response(qr.png_visita(v.token), mimetype="image/png")

@portal_bp.route("/portal/mi-casa/personas", methods=["POST"])
@residente_required
def actualizar_personas():
    residente = services.datos_residente(session["residente_id"])
    personas = request.form.get("personas", "").strip()
    if personas and not personas.isdigit():
        flash("Ingresa un número válido", "error")
    else:
        services.actualizar_personas(residente.casa_id, personas or None)
        flash("Datos de la casa actualizados", "success")
    return redirect(url_for("portal.inicio"))

@portal_bp.route("/portal/cuotas/<int:id>/pagar", methods=["GET", "POST"])
@residente_required
def pagar_cuota(id):
    residente = services.datos_residente(session["residente_id"])
    cuota = services.obtener_cuota_de_casa(id, residente.casa_id)
    if not cuota:
        flash("Cuota no encontrada", "error")
        return redirect(url_for("portal.cuotas"))
    if cuota.estado == "pagado":
        flash("Esta cuota ya está pagada", "error")
        return redirect(url_for("portal.cuotas"))
    if cuota.estado == "en_revision":
        flash("Esta cuota ya tiene una transferencia en revisión", "error")
        return redirect(url_for("portal.cuotas"))

    from modules.pagos.services import calcular_recargo, total_con_recargo
    cuota.recargo_calc = calcular_recargo(cuota)
    cuota.total = total_con_recargo(cuota)

    if request.method == "POST":
        metodo = request.form.get("metodo_pago", "")
        archivo = request.files.get("comprobante")
        cu, err = services.pagar_cuota(
            id, residente.casa_id, metodo,
            current_app.config["UPLOAD_FOLDER"],
            archivo=archivo if metodo == "transferencia" else None,
        )
        if err:
            flash(err, "error")
            return render_template("portal/pago_form.html", cuota=cuota,
                                   residente=residente, meses=MESES)
        if cu.estado == "en_revision":
            flash(f"Comprobante enviado — {MESES[cu.mes]} {cu.anio}. "
                  "Tu pago quedó en revisión hasta que el administrador lo confirme.",
                  "success")
        else:
            flash(f"Pago registrado correctamente — {MESES[cu.mes]} {cu.anio}", "success")
        return redirect(url_for("portal.cuotas"))

    return render_template("portal/pago_form.html", cuota=cuota,
                           residente=residente, meses=MESES)

@portal_bp.route("/portal/multas/<int:id>/pagar", methods=["POST"])
@residente_required
def pagar_multa(id):
    residente = services.datos_residente(session["residente_id"])
    _, err = services.pagar_multa(id, residente.casa_id)
    flash(err or "Multa pagada correctamente", "error" if err else "success")
    return redirect(url_for("portal.cuotas"))

@portal_bp.route("/portal/visitas/nueva", methods=["GET", "POST"])
@residente_required
def nueva_visita():
    residente = services.datos_residente(session["residente_id"])
    if request.method == "POST":
        err = services.solicitar_visita(
            casa_id=residente.casa_id,
            nombre_visitante=request.form["nombre_visitante"],
            cedula_visitante=request.form.get("cedula_visitante", ""),
            motivo=request.form.get("motivo", ""),
            placa_vehiculo=request.form.get("placa_vehiculo", ""),
            autorizado_por=residente.nombre,
        )
        if err:
            flash(err, "error")
            return render_template("portal/visita_form.html", residente=residente)
        flash("Solicitud enviada. El guardia la aprobará cuando llegue tu visitante.",
              "success")
        return redirect(url_for("portal.visitas"))
    return render_template("portal/visita_form.html", residente=residente)
