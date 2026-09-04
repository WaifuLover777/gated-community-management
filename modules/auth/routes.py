from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from modules.auth import services
from models import Residente
from extensions import limiter

auth_bp = Blueprint("auth", __name__)

def _redirect_por_rol(rol):
    if rol == "admin":
        return redirect(url_for("dashboard.inicio"))
    if rol == "guardia":
        return redirect(url_for("guardia.inicio"))
    if rol == "residente":
        return redirect(url_for("portal.inicio"))
    return redirect(url_for("auth.login"))

@auth_bp.route("/login", methods=["GET", "POST"])
@limiter.limit("10 per minute", methods=["POST"])
def login():
    if request.method == "POST":
        usuario = services.autenticar(request.form["email"], request.form["password"])
        if usuario:
            session.permanent = True
            session["usuario"] = usuario.nombre
            session["rol"] = usuario.rol
            session["usuario_id"] = usuario.id
            session["residente_id"] = usuario.residente_id
            return _redirect_por_rol(usuario.rol)
        flash("Credenciales incorrectas", "error")
    return render_template("login.html")

@auth_bp.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "GET":
        return render_template("registro_pin.html")

    paso = request.form.get("paso", "1")

    if paso == "1":
        pin = request.form.get("pin", "").strip()
        casa = services.casa_por_pin(pin)
        if not casa:
            flash("PIN inválido o ya utilizado. Solicítalo al administrador.", "error")
            return render_template("registro_pin.html")

        ya_tiene = Residente.query.filter_by(casa_id=casa.id, tipo="propietario", activo=True).first()
        if ya_tiene:
            flash("Esta villa ya tiene un propietario activo. No se puede registrar otro. Contacta al administrador.", "error")
            return render_template("registro_pin.html")
        return render_template("registro.html", casa=casa, pin=pin)

    pin = request.form.get("pin", "").strip()
    casa = services.casa_por_pin(pin)
    if not casa:
        flash("PIN inválido o ya utilizado. Solicítalo al administrador.", "error")
        return render_template("registro_pin.html")

    password = request.form.get("password", "")
    confirmar = request.form.get("confirmar", "")
    if password != confirmar:
        flash("Las contraseñas no coinciden", "error")
        return render_template("registro.html", casa=casa, pin=pin)
    if len(password) < 6:
        flash("La contraseña debe tener al menos 6 caracteres", "error")
        return render_template("registro.html", casa=casa, pin=pin)

    usuario, error = services.registrar_residente(
        nombre=request.form.get("nombre", "").strip(),
        cedula=request.form.get("cedula", "").strip(),
        telefono=request.form.get("telefono", "").strip(),
        email=request.form.get("email", "").strip(),
        password=password,
        pin=pin,
        tipo=request.form.get("tipo", ""),
    )
    if error:
        flash(error, "error")

        casa = services.casa_por_pin(pin)
        if not casa:
            return render_template("registro_pin.html")
        return render_template("registro.html", casa=casa, pin=pin)
    flash("¡Registro exitoso! Ya puedes iniciar sesión.", "success")
    return redirect(url_for("auth.login"))

@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))
