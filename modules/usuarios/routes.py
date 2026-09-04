from flask import Blueprint, render_template, request, redirect, url_for, flash
from core.decorators import admin_required
from modules.usuarios import services

usuarios_bp = Blueprint("usuarios", __name__)

@usuarios_bp.route("/usuarios")
@admin_required
def lista():
    return render_template("usuarios.html", usuarios=services.listar())

@usuarios_bp.route("/usuarios/nuevo", methods=["GET", "POST"])
@admin_required
def nuevo():
    if request.method == "POST":
        _, error = services.crear(
            nombre=request.form["nombre"],
            email=request.form["email"],
            password=request.form["password"],
            rol=request.form["rol"],
            residente_id=request.form.get("residente_id"),
        )
        if error:
            flash(error, "error")
        else:
            flash("Usuario creado correctamente", "success")
            return redirect(url_for("usuarios.lista"))
    return render_template("usuario_form.html", residentes=services.residentes_disponibles())

@usuarios_bp.route("/usuarios/eliminar/<int:id>")
@admin_required
def eliminar(id):
    ok, error = services.eliminar(id)
    flash("Usuario eliminado" if ok else error, "success" if ok else "error")
    return redirect(url_for("usuarios.lista"))
