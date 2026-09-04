from flask import (Blueprint, render_template, request, redirect, url_for,
                   session, flash, current_app)
from core.decorators import residente_required, admin_required
from modules.incidencias import services
from modules.portal import services as portal_services

incidencias_bp = Blueprint("incidencias", __name__)


@incidencias_bp.route("/portal/incidencias")
@residente_required
def mis_incidencias():
    residente = portal_services.datos_residente(session["residente_id"])
    return render_template("portal/incidencias.html",
                           incidencias=services.listar_de_casa(residente.casa_id),
                           categorias=services.CATEGORIAS)

@incidencias_bp.route("/portal/incidencias/nueva", methods=["POST"])
@residente_required
def nueva_incidencia():
    residente = portal_services.datos_residente(session["residente_id"])
    err = services.crear(
        casa_id=residente.casa_id,
        residente_id=residente.id,
        titulo=request.form.get("titulo", ""),
        descripcion=request.form.get("descripcion", ""),
        categoria=request.form.get("categoria", "general"),
        archivo=request.files.get("foto"),
        upload_folder=current_app.config["UPLOAD_FOLDER"],
    )
    flash(err or "Incidencia reportada. El administrador le dará seguimiento.",
          "error" if err else "success")
    return redirect(url_for("incidencias.mis_incidencias"))


@incidencias_bp.route("/incidencias")
@admin_required
def admin_lista():
    estado = request.args.get("estado", "")
    return render_template("incidencias_admin.html",
                           incidencias=services.listar_todas(estado or None),
                           estado=estado, estados=services.ESTADOS)

@incidencias_bp.route("/incidencias/<int:id>/estado", methods=["POST"])
@admin_required
def admin_estado(id):
    err = services.actualizar_estado(
        id,
        estado=request.form.get("estado", ""),
        respuesta=request.form.get("respuesta", ""),
    )
    flash(err or "Incidencia actualizada", "error" if err else "success")
    return redirect(url_for("incidencias.admin_lista"))
