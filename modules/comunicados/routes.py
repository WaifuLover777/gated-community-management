from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from core.decorators import login_required, admin_required
from modules.comunicados import services

comunicados_bp = Blueprint("comunicados", __name__)

@comunicados_bp.route("/")
@login_required
def lista():
    tipo = request.args.get("tipo", "")

    es_admin = session.get("rol") == "admin"
    return render_template("comunicados.html",
                           comunicados=services.listar(tipo or None,
                                                       solo_publicados=not es_admin),
                           tipo=tipo, es_admin=es_admin)

@comunicados_bp.route("/nuevo", methods=["GET", "POST"])
@admin_required
def nuevo():
    if request.method == "POST":
        err = services.crear(
            titulo=request.form["titulo"],
            contenido=request.form["contenido"],
            tipo=request.form.get("tipo", "anuncio"),
            publicado_por=session.get("usuario", ""),
            fecha_publicacion=request.form.get("fecha_publicacion", ""),
        )
        if err:
            flash(err, "error")
            return render_template("comunicado_form.html", comunicado=None)
        flash("Comunicado guardado", "success")
        return redirect(url_for("comunicados.lista"))
    return render_template("comunicado_form.html", comunicado=None)

@comunicados_bp.route("/editar/<int:id>", methods=["GET", "POST"])
@admin_required
def editar(id):
    if request.method == "POST":
        err = services.actualizar(
            id,
            titulo=request.form["titulo"],
            contenido=request.form["contenido"],
            tipo=request.form.get("tipo", "anuncio"),
            fecha_publicacion=request.form.get("fecha_publicacion", ""),
        )
        if err:
            flash(err, "error")
            return render_template("comunicado_form.html", comunicado=services.obtener(id))
        flash("Comunicado actualizado", "success")
        return redirect(url_for("comunicados.lista"))
    return render_template("comunicado_form.html", comunicado=services.obtener(id))

@comunicados_bp.route("/archivar/<int:id>")
@admin_required
def archivar(id):
    services.archivar(id)
    flash("Comunicado archivado", "success")
    return redirect(url_for("comunicados.lista"))
