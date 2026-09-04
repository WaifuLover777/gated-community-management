from flask import Blueprint, render_template, request, redirect, url_for, flash
from core.decorators import admin_required
from modules.multas import services
from models import Casa

multas_bp = Blueprint("multas", __name__)

@multas_bp.route("/multas")
@admin_required
def lista():
    estado = request.args.get("estado", "")
    casas = Casa.query.order_by(Casa.manzana, Casa.numero).all()
    return render_template("multas_admin.html",
                           multas=services.listar(estado or None),
                           casas=casas, estado=estado)

@multas_bp.route("/multas/nueva", methods=["POST"])
@admin_required
def nueva():
    err = services.crear(
        casa_id=request.form.get("casa_id", type=int),
        motivo=request.form.get("motivo", ""),
        descripcion=request.form.get("descripcion", ""),
        monto=request.form.get("monto", ""),
    )
    flash(err or "Multa registrada", "error" if err else "success")
    return redirect(url_for("multas.lista"))

@multas_bp.route("/multas/<int:id>/estado", methods=["POST"])
@admin_required
def estado(id):
    err = services.cambiar_estado(id, request.form.get("estado", ""))
    flash(err or "Multa actualizada", "error" if err else "success")
    return redirect(url_for("multas.lista"))
