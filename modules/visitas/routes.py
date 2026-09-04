from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from core.decorators import guardia_required
from modules.visitas import services
from modules.residentes import services as res_services

visitas_bp = Blueprint("visitas", __name__)

@visitas_bp.route("/")
@guardia_required
def lista():
    filtro_fecha = request.args.get("fecha", "")
    filtro_casa = request.args.get("casa", "")
    visitas = services.listar(filtro_fecha or None, filtro_casa or None)
    return render_template("visitas.html", visitas=visitas, casas=res_services.casas_select(),
                           filtro_fecha=filtro_fecha, filtro_casa=filtro_casa)

@visitas_bp.route("/nueva", methods=["GET", "POST"])
@guardia_required
def nueva():
    if request.method == "POST":
        err = services.registrar(
            casa_id=request.form["casa_id"],
            nombre_visitante=request.form["nombre_visitante"],
            cedula_visitante=request.form.get("cedula_visitante", ""),
            motivo=request.form.get("motivo", ""),
            placa_vehiculo=request.form.get("placa_vehiculo", ""),
            autorizado_por=session.get("usuario", ""),
            guardia_id=session.get("usuario_id"),
        )
        if err:
            flash(err, "error")
            return render_template("visita_form.html", casas=res_services.casas_select())
        flash("Visita registrada correctamente", "success")
        return redirect(url_for("visitas.lista"))
    return render_template("visita_form.html", casas=res_services.casas_select())

@visitas_bp.route("/salida/<int:id>")
@guardia_required
def registrar_salida(id):
    services.registrar_salida(id, guardia_id=session.get("usuario_id"))
    flash("Salida registrada", "success")
    return redirect(url_for("visitas.lista"))
