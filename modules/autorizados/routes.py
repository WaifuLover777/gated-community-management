from flask import (Blueprint, render_template, request, redirect, url_for,
                   session, flash, Response, abort)
from core.decorators import residente_required
from modules.autorizados import services
from modules.portal import services as portal_services

autorizados_bp = Blueprint("autorizados", __name__)

@autorizados_bp.route("/portal/autorizados")
@residente_required
def lista():
    residente = portal_services.datos_residente(session["residente_id"])
    return render_template("portal/autorizados.html",
                           autorizados=services.listar_de_casa(residente.casa_id),
                           relaciones=services.RELACIONES)

@autorizados_bp.route("/portal/autorizados/nuevo", methods=["POST"])
@residente_required
def nuevo():
    residente = portal_services.datos_residente(session["residente_id"])
    err = services.crear(
        casa_id=residente.casa_id,
        residente_id=residente.id,
        nombre=request.form.get("nombre", ""),
        cedula=request.form.get("cedula", ""),
        relacion=request.form.get("relacion", "otro"),
        vigencia_desde=request.form.get("vigencia_desde", ""),
        vigencia_hasta=request.form.get("vigencia_hasta", ""),
    )
    flash(err or "Persona autorizada registrada", "error" if err else "success")
    return redirect(url_for("autorizados.lista"))

@autorizados_bp.route("/portal/autorizados/<int:id>/alternar", methods=["POST"])
@residente_required
def alternar(id):
    residente = portal_services.datos_residente(session["residente_id"])
    err = services.alternar(id, residente.casa_id)
    flash(err or "Estado actualizado", "error" if err else "success")
    return redirect(url_for("autorizados.lista"))

@autorizados_bp.route("/portal/autorizados/<int:id>/qr")
@residente_required
def qr(id):
    from core.reconocimiento import qr as qr_engine
    residente = portal_services.datos_residente(session["residente_id"])
    a = services.obtener(id, residente.casa_id)
    if not a:
        abort(404)
    return Response(qr_engine.png_autorizado(a.token), mimetype="image/png")
