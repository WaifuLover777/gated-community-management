from flask import (Blueprint, render_template, request, redirect, url_for,
                   session, flash, current_app)
from core.decorators import guardia_required
from modules.guardia import services
from modules.visitas import services as visitas_services

guardia_bp = Blueprint("guardia", __name__)

@guardia_bp.route("/guardia")
@guardia_required
def inicio():
    return render_template("guardia/inicio.html",
                           visitas=services.visitas_hoy(),
                           dentro=services.contar_dentro())

@guardia_bp.route("/guardia/visitas/salida/<int:id>")
@guardia_required
def salida(id):
    visitas_services.registrar_salida(id, guardia_id=session.get("usuario_id"))
    flash("Salida registrada", "success")
    return redirect(url_for("guardia.inicio"))

@guardia_bp.route("/guardia/vehiculos")
@guardia_required
def vehiculos():
    placa = request.args.get("placa", "").strip().upper()
    vehiculo = services.verificar_placa(placa) if placa else None
    return render_template("guardia/vehiculos.html", vehiculo=vehiculo, placa=placa)

@guardia_bp.route("/guardia/visitas")
@guardia_required
def visitas_pendientes():
    return render_template("guardia/visitas_pendientes.html",
                           visitas=services.visitas_pendientes())

@guardia_bp.route("/guardia/visitas/autorizar/<int:id>", methods=["POST"])
@guardia_required
def autorizar_entrada(id):
    visita, err = services.autorizar_entrada(id, guardia_id=session.get("usuario_id"))
    if err:
        flash(err, "error")
    else:
        flash(f"Entrada autorizada — {visita.nombre_visitante}", "success")
    return redirect(url_for("guardia.visitas_pendientes"))

@guardia_bp.route("/guardia/residentes")
@guardia_required
def residentes():
    filtro = request.args.get("filtro", "")
    return render_template("guardia/residentes.html",
                           residentes=services.buscar_residentes(filtro), filtro=filtro)

@guardia_bp.route("/guardia/comunicados")
@guardia_required
def comunicados():
    return render_template("guardia/comunicados.html",
                           comunicados=services.comunicados_para_guardia())

@guardia_bp.route("/guardia/novedades")
@guardia_required
def novedades():
    return render_template("guardia/novedades.html",
                           novedades=services.listar_novedades(),
                           categorias=services.CATEGORIAS_NOVEDAD)

@guardia_bp.route("/guardia/novedades/nueva", methods=["POST"])
@guardia_required
def nueva_novedad():
    _, err = services.crear_novedad(
        guardia_id=session.get("usuario_id"),
        categoria=request.form.get("categoria", "general"),
        texto=request.form.get("texto", ""),
        tipo=request.form.get("tipo", "novedad"),
        archivo=request.files.get("foto"),
        upload_folder=current_app.config["UPLOAD_FOLDER"],
    )
    flash(err or "Novedad registrada", "error" if err else "success")
    return redirect(url_for("guardia.novedades"))

@guardia_bp.route("/guardia/novedades/<int:id>/editar", methods=["POST"])
@guardia_required
def editar_novedad(id):
    err = services.actualizar_novedad(
        id,
        categoria=request.form.get("categoria", "general"),
        texto=request.form.get("texto", ""),
    )
    flash(err or "Novedad actualizada", "error" if err else "success")
    return redirect(url_for("guardia.novedades"))
