from flask import (Blueprint, render_template, request, jsonify, session,
                   Response, redirect, url_for, flash)
from core.decorators import guardia_required, admin_required
from core import camaras
from core.reconocimiento import qr, placas, rostros
from modules.garita import services

garita_bp = Blueprint("garita", __name__)

@garita_bp.route("/guardia/control")
@guardia_required
def control():
    cams = {n: camaras.backend_de(n) for n in ("frontal", "trasera", "cabina")}
    return render_template("guardia/control.html", camaras=cams)

@garita_bp.route("/guardia/control/snapshot/<camara>")
@guardia_required
def snapshot(camara):
    data, _ = camaras.capturar(camara, request.args.get("backend"),
                               request.args.get("fuente"))
    if not data:
        return ("", 404)
    return Response(data, mimetype="image/jpeg")

@garita_bp.route("/guardia/control/qr", methods=["POST"])
@guardia_required
def escanear_qr():
    archivo = request.files.get("imagen")
    if archivo and archivo.filename:
        imagen = archivo.read()
    else:
        camara = request.form.get("camara", "cabina")
        imagen, _ = camaras.capturar(camara, request.form.get("backend"),
                                     request.form.get("fuente"))
    if not imagen:
        return jsonify({"ok": False, "mensaje": "No se obtuvo imagen de la cámara."}), 200

    contenido = qr.leer_qr(imagen)
    if not contenido:
        return jsonify({"ok": False, "mensaje": "No se detectó ningún QR en la imagen."}), 200

    res = services.validar_qr(contenido, guardia_id=session.get("usuario_id"))
    return jsonify(res), 200

def _leer_placa_de(camara, archivo, backend=None, fuente=None):
    """Obtiene (placa, foto_bytes) de un archivo subido o de la cámara (modo sim)."""
    if archivo:
        data = archivo.read()
        lectura = placas.leer_placa(data, pista=archivo.filename)
        return (lectura or {}).get("placa"), data
    data, _ = camaras.capturar(camara, backend, fuente)
    pista = camaras.nombre_archivo_emulador(camara)
    lectura = placas.leer_placa(data, pista=pista)
    return (lectura or {}).get("placa"), data

@garita_bp.route("/guardia/control/placas", methods=["POST"])
@guardia_required
def escanear_placas():
    tipo = request.form.get("tipo", "entrada")
    pf = request.form.get("placa_frontal", "").strip()
    pt = request.form.get("placa_trasera", "").strip()
    backend, fuente = request.form.get("backend"), request.form.get("fuente")
    foto = None
    if not pf:
        pf, foto = _leer_placa_de("frontal", request.files.get("img_frontal"), backend, fuente)
    if not pt:
        pt, foto2 = _leer_placa_de("trasera", request.files.get("img_trasera"), backend, fuente)
        foto = foto or foto2
    res = services.procesar_placas(
        placa_frontal=pf, placa_trasera=pt, tipo=tipo,
        foto_bytes=foto, guardia_id=session.get("usuario_id"))
    return jsonify(res), 200

@garita_bp.route("/guardia/control/rostro", methods=["POST"])
@guardia_required
def escanear_rostro():
    archivo = request.files.get("imagen")
    if archivo and archivo.filename:
        imagen = archivo.read()
    else:
        imagen, _ = camaras.capturar("cabina", request.form.get("backend"),
                                     request.form.get("fuente"))
    if not imagen:
        return jsonify({"ok": False, "mensaje": "No se obtuvo imagen de cabina."}), 200
    res = services.procesar_rostros(imagen, guardia_id=session.get("usuario_id"))
    return jsonify(res), 200


@garita_bp.route("/lista-negra")
@admin_required
def lista_negra():
    return render_template("lista_negra_admin.html",
                           entradas=services.listar_lista_negra())

@garita_bp.route("/lista-negra/agregar", methods=["POST"])
@admin_required
def lista_negra_agregar():
    err = services.agregar_lista_negra(request.form.get("placa", ""),
                                       request.form.get("motivo", ""))
    flash(err or "Placa agregada a la lista negra", "error" if err else "success")
    return redirect(url_for("garita.lista_negra"))

@garita_bp.route("/lista-negra/<int:id>/alternar", methods=["POST"])
@admin_required
def lista_negra_alternar(id):
    services.alternar_lista_negra(id)
    flash("Estado actualizado", "success")
    return redirect(url_for("garita.lista_negra"))
