from datetime import date
from flask import Blueprint, render_template, request, redirect, url_for, flash, make_response
from core.decorators import admin_required
from core.utils import MESES
from modules.pagos import services
from modules.residentes import services as res_services

pagos_bp = Blueprint("pagos", __name__)

@pagos_bp.route("/")
@admin_required
def lista():
    if "anio" in request.args:
        anio_raw = request.args.get("anio", "")
        anio = int(anio_raw) if anio_raw else None
    else:
        anio = date.today().year
    mes = request.args.get("mes", "")
    estado = request.args.get("estado", "")
    casa = request.args.get("casa", "")
    cuotas = services.listar_cuotas(anio, mes or None, estado or None, casa or None)
    return render_template("pagos.html", cuotas=cuotas, anio=anio, mes=mes,
                           estado=estado, casa=casa, meses=MESES, totales=services.totales(anio),
                           anios=services.anios_disponibles())

@pagos_bp.route("/generar", methods=["GET", "POST"])
@admin_required
def generar():
    if request.method == "POST":
        try:
            mes = int(request.form["mes"])
            anio = int(request.form["anio"])
        except (ValueError, KeyError):
            flash("Mes o año inválido.", "error")
            return redirect(url_for("pagos.generar"))
        generadas, err = services.generar(mes, anio)
        if err:
            flash(err, "error")
            return redirect(url_for("pagos.generar"))
        flash(f"Se generaron cuotas para {generadas} casas — {MESES[mes]} {anio}", "success")
        return redirect(url_for("pagos.lista"))
    return render_template("pagos_generar.html", meses=MESES,
                           anio_actual=date.today().year, mes_actual=date.today().month)

@pagos_bp.route("/reporte")
@admin_required
def reporte():
    if "anio" in request.args:
        anio_raw = request.args.get("anio", "")
        anio = int(anio_raw) if anio_raw else None
    else:
        anio = date.today().year
    mes = request.args.get("mes", "")
    datos = services.reporte_cobranza(anio, int(mes) if mes else None)
    return render_template("pagos_reporte.html", reporte=datos, anio=anio, mes=mes,
                           meses=MESES, anios=services.anios_disponibles())

@pagos_bp.route("/extraordinaria", methods=["GET", "POST"])
@admin_required
def extraordinaria():
    hoy = date.today()
    if request.method == "POST":
        try:
            mes = int(request.form["mes"])
            anio = int(request.form["anio"])
        except (ValueError, KeyError):
            flash("Mes o año inválido.", "error")
            return redirect(url_for("pagos.extraordinaria"))
        ambito = request.form.get("ambito", "todas")
        casa_id = None
        if ambito == "casa":
            try:
                casa_id = int(request.form.get("casa_id", ""))
            except ValueError:
                flash("Selecciona una casa válida.", "error")
                return redirect(url_for("pagos.extraordinaria"))
        generadas, err = services.generar_extraordinaria(
            concepto=request.form.get("concepto", ""),
            monto=request.form.get("monto", ""),
            anio=anio, mes=mes, casa_id=casa_id,
        )
        if err:
            flash(err, "error")
            return redirect(url_for("pagos.extraordinaria"))
        flash(f"Cuota extraordinaria generada para {generadas} casa(s) — "
              f"{MESES[mes]} {anio}", "success")
        return redirect(url_for("pagos.lista"))
    return render_template("pagos_extraordinaria.html", meses=MESES,
                           anio_actual=hoy.year, mes_actual=hoy.month,
                           casas=res_services.casas_select())

@pagos_bp.route("/comprobante/<int:id>")
@admin_required
def comprobante(id):
    from modules.pagos.pdf import generar_comprobante
    cuota = services.obtener_cuota(id)
    if not cuota or cuota.estado != "pagado":
        flash("Solo se generan comprobantes de cuotas pagadas", "error")
        return redirect(url_for("pagos.lista"))
    pdf = generar_comprobante(cuota)
    resp = make_response(pdf.read())
    resp.headers["Content-Type"] = "application/pdf"
    filename = f"comprobante-{cuota.casa.manzana}{cuota.casa.numero}-{MESES[cuota.mes]}-{cuota.anio}.pdf"
    resp.headers["Content-Disposition"] = f"attachment; filename={filename}"
    return resp

@pagos_bp.route("/confirmar/<int:id>", methods=["POST"])
@admin_required
def confirmar(id):
    _, err = services.confirmar_transferencia(id)
    flash(err or "Transferencia confirmada. Cuota marcada como pagada.",
          "error" if err else "success")
    return redirect(url_for("pagos.lista"))

@pagos_bp.route("/rechazar/<int:id>", methods=["POST"])
@admin_required
def rechazar(id):
    _, err = services.rechazar_transferencia(id)
    flash(err or "Comprobante rechazado. La cuota vuelve a pendiente.",
          "error" if err else "success")
    return redirect(url_for("pagos.lista"))
