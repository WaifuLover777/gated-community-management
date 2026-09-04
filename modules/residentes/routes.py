from flask import Blueprint, render_template, request, redirect, url_for, flash
from core.decorators import admin_required
from modules.residentes import services

residentes_bp = Blueprint("residentes", __name__)

@residentes_bp.route("/casas")
@admin_required
def casas():
    return render_template("casas.html", casas=services.listar_casas())

@residentes_bp.route("/casas/nueva", methods=["GET", "POST"])
@admin_required
def nueva_casa():
    if request.method == "POST":
        err = services.crear_casa(
            numero=request.form["numero"], manzana=request.form["manzana"],
            tipo=request.form.get("tipo"), color=request.form.get("color"),
            area_m2=request.form.get("area_m2"), alicuota=request.form.get("alicuota"),
            estado=request.form.get("estado", "ocupada"),
            capacidad=request.form.get("capacidad"),
            personas=request.form.get("personas"),
        )
        if err:
            flash(err, "error")
            return render_template("casa_form.html", casa=None)
        flash("Casa registrada correctamente", "success")
        return redirect(url_for("residentes.casas"))
    return render_template("casa_form.html", casa=None)

@residentes_bp.route("/casas/editar/<int:id>", methods=["GET", "POST"])
@admin_required
def editar_casa(id):
    if request.method == "POST":
        err = services.actualizar_casa(
            id, numero=request.form["numero"], manzana=request.form["manzana"],
            tipo=request.form.get("tipo"), color=request.form.get("color"),
            area_m2=request.form.get("area_m2"), alicuota=request.form.get("alicuota"),
            estado=request.form.get("estado", "ocupada"),
            capacidad=request.form.get("capacidad"),
            personas=request.form.get("personas"),
        )
        if err:
            flash(err, "error")
            return render_template("casa_form.html", casa=services.obtener_casa(id))
        flash("Casa actualizada", "success")
        return redirect(url_for("residentes.casas"))
    return render_template("casa_form.html", casa=services.obtener_casa(id))

@residentes_bp.route("/casas/<int:id>/pin", methods=["POST"])
@admin_required
def generar_pin_casa(id):
    pin, err = services.generar_pin_casa(id)
    if err:
        flash(err, "error")
    else:
        casa = services.obtener_casa(id)
        flash(f"PIN de registro para la villa {casa.manzana}-{casa.numero}: "
              f"{pin} — envíalo al residente (es de un solo uso).", "success")
    return redirect(url_for("residentes.casas"))

@residentes_bp.route("/")
@admin_required
def lista():
    filtro = request.args.get("filtro", "")
    return render_template("residentes.html",
                           residentes=services.listar_residentes(filtro), filtro=filtro)

@residentes_bp.route("/nuevo", methods=["GET", "POST"])
@admin_required
def nuevo():
    if request.method == "POST":
        err = services.crear_residente(
            casa_id=request.form["casa_id"], nombre=request.form["nombre"],
            cedula=request.form["cedula"], telefono=request.form.get("telefono", ""),
            email=request.form.get("email", ""), tipo=request.form["tipo"],
            fecha_ingreso=request.form.get("fecha_ingreso", ""),
        )
        if err:
            flash(err, "error")
            return render_template("residente_form.html", residente=None,
                                   casas=services.casas_select())
        flash("Residente registrado correctamente", "success")
        return redirect(url_for("residentes.lista"))
    return render_template("residente_form.html", residente=None, casas=services.casas_select())

@residentes_bp.route("/editar/<int:id>", methods=["GET", "POST"])
@admin_required
def editar(id):
    if request.method == "POST":
        err = services.actualizar_residente(
            id, casa_id=request.form["casa_id"], nombre=request.form["nombre"],
            cedula=request.form["cedula"], telefono=request.form.get("telefono", ""),
            email=request.form.get("email", ""), tipo=request.form["tipo"],
        )
        if err:
            flash(err, "error")
            return render_template("residente_form.html",
                                   residente=services.obtener_residente(id),
                                   casas=services.casas_select())
        flash("Residente actualizado", "success")
        return redirect(url_for("residentes.lista"))
    return render_template("residente_form.html",
                           residente=services.obtener_residente(id),
                           casas=services.casas_select())

@residentes_bp.route("/eliminar/<int:id>")
@admin_required
def eliminar(id):
    services.dar_de_baja(id)
    flash("Residente dado de baja", "success")
    return redirect(url_for("residentes.lista"))

@residentes_bp.route("/vehiculos")
@admin_required
def vehiculos():
    return render_template("vehiculos.html", vehiculos=services.listar_vehiculos())

@residentes_bp.route("/vehiculos/nuevo", methods=["GET", "POST"])
@admin_required
def nuevo_vehiculo():
    if request.method == "POST":
        err = services.crear_vehiculo(
            residente_id=request.form["residente_id"], placa=request.form["placa"],
            marca=request.form.get("marca", ""), modelo=request.form.get("modelo", ""),
            color=request.form.get("color", ""),
        )
        if err:
            flash(err, "error")
            return render_template("vehiculo_form.html",
                                   residentes=services.residentes_para_select())
        flash("Vehículo registrado", "success")
        return redirect(url_for("residentes.vehiculos"))
    return render_template("vehiculo_form.html", residentes=services.residentes_para_select())
