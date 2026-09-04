from datetime import date
from flask import (Blueprint, render_template, request, redirect, url_for,
                  session, flash)
from core.decorators import residente_required, admin_required
from modules.reservas import services
from modules.portal import services as portal_services

reservas_bp = Blueprint("reservas", __name__)


@reservas_bp.route("/portal/reservas")
@residente_required
def mis_reservas():
    residente = portal_services.datos_residente(session["residente_id"])
    return render_template("portal/reservas.html",
                           areas=services.listar_areas(solo_activas=True),
                           reservas=services.reservas_de_casa(residente.casa_id),
                           hoy=date.today().isoformat())

@reservas_bp.route("/portal/reservas/nueva", methods=["POST"])
@residente_required
def nueva_reserva():
    residente = portal_services.datos_residente(session["residente_id"])
    err = services.crear_reserva(
        area_id=request.form.get("area_id", type=int),
        casa_id=residente.casa_id,
        residente_id=residente.id,
        fecha=request.form.get("fecha", ""),
        hora_inicio=request.form.get("hora_inicio", ""),
        hora_fin=request.form.get("hora_fin", ""),
    )
    flash(err or "Reserva confirmada", "error" if err else "success")
    return redirect(url_for("reservas.mis_reservas"))

@reservas_bp.route("/portal/reservas/<int:id>/cancelar", methods=["POST"])
@residente_required
def cancelar_reserva(id):
    residente = portal_services.datos_residente(session["residente_id"])
    err = services.cancelar_reserva(id, residente.casa_id)
    flash(err or "Reserva cancelada", "error" if err else "success")
    return redirect(url_for("reservas.mis_reservas"))


@reservas_bp.route("/areas")
@admin_required
def admin_areas():
    return render_template("areas_admin.html", areas=services.listar_areas())

@reservas_bp.route("/areas/nueva", methods=["POST"])
@admin_required
def admin_nueva_area():
    err = services.crear_area(
        nombre=request.form.get("nombre", ""),
        descripcion=request.form.get("descripcion", ""),
        hora_apertura=request.form.get("hora_apertura", ""),
        hora_cierre=request.form.get("hora_cierre", ""),
    )
    flash(err or "Área creada", "error" if err else "success")
    return redirect(url_for("reservas.admin_areas"))

@reservas_bp.route("/areas/<int:id>/alternar", methods=["POST"])
@admin_required
def admin_alternar_area(id):
    services.alternar_area(id)
    flash("Estado del área actualizado", "success")
    return redirect(url_for("reservas.admin_areas"))
