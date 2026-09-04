from flask import (Blueprint, render_template, request, redirect, url_for,
                   session, flash, current_app)
from core.decorators import guardia_required, residente_required
from modules.paqueteria import services
from modules.portal import services as portal_services
from models import Casa

paqueteria_bp = Blueprint("paqueteria", __name__)


@paqueteria_bp.route("/guardia/paqueteria")
@guardia_required
def guardia_lista():
    estado = request.args.get("estado", "")
    casas = Casa.query.order_by(Casa.manzana, Casa.numero).all()
    return render_template("guardia/paqueteria.html",
                           paquetes=services.listar(estado or None),
                           casas=casas, estado=estado)

@paqueteria_bp.route("/guardia/paqueteria/nuevo", methods=["POST"])
@guardia_required
def registrar():
    err = services.registrar(
        casa_id=request.form.get("casa_id", type=int),
        descripcion=request.form.get("descripcion", ""),
        remitente=request.form.get("remitente", ""),
        recibido_por=session.get("usuario", ""),
        archivo=request.files.get("foto"),
        upload_folder=current_app.config["UPLOAD_FOLDER"],
    )
    flash(err or "Paquete registrado y residente notificado", "error" if err else "success")
    return redirect(url_for("paqueteria.guardia_lista"))

@paqueteria_bp.route("/guardia/paqueteria/<int:id>/entregar", methods=["POST"])
@guardia_required
def entregar(id):
    err = services.marcar_entregado(id, retirado_por=request.form.get("retirado_por", ""))
    flash(err or "Paquete marcado como entregado", "error" if err else "success")
    return redirect(url_for("paqueteria.guardia_lista"))


@paqueteria_bp.route("/portal/paqueteria")
@residente_required
def mis_paquetes():
    residente = portal_services.datos_residente(session["residente_id"])
    return render_template("portal/paqueteria.html",
                           paquetes=services.listar_de_casa(residente.casa_id))
