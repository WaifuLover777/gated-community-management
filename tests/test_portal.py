from modules.portal import services
from models import Cuota, Vehiculo, Visita, Multa
from extensions import db


def test_deuda_incluye_cuotas_y_multas(app):
    with app.app_context():
        casa_id = app.config["SEED"]["casa_id"]
        base = services.deuda_de_casa(casa_id)
        assert base["total"] > 0
        db.session.add(Multa(casa_id=casa_id, motivo="Ruido", monto=20.0,
                             estado="pendiente"))
        db.session.commit()
        con_multa = services.deuda_de_casa(casa_id)
        assert con_multa["multas"] == 20.0
        assert round(con_multa["total"] - base["total"], 2) == 20.0


def test_pagar_cuota_online(app, tmp_path):
    with app.app_context():
        casa_id = app.config["SEED"]["casa_id"]
        cu = Cuota.query.filter_by(casa_id=casa_id, estado="pendiente").first()
        out, err = services.pagar_cuota(cu.id, casa_id, "online", str(tmp_path))
        assert err is None and out.estado == "pagado"


def test_pagar_cuota_ya_pagada(app, tmp_path):
    with app.app_context():
        casa_id = app.config["SEED"]["casa_id"]
        cu = Cuota.query.filter_by(casa_id=casa_id, estado="pagado").first()
        out, err = services.pagar_cuota(cu.id, casa_id, "online", str(tmp_path))
        assert out is None and err is not None


def test_pagar_multa(app):
    with app.app_context():
        casa_id = app.config["SEED"]["casa_id"]
        m = Multa(casa_id=casa_id, motivo="Ruido", monto=20.0, estado="pendiente")
        db.session.add(m)
        db.session.commit()
        out, err = services.pagar_multa(m.id, casa_id)
        assert err is None and out.estado == "pagada" and out.fecha_pago


def test_pagar_multa_ya_pagada(app):
    with app.app_context():
        casa_id = app.config["SEED"]["casa_id"]
        m = Multa(casa_id=casa_id, motivo="Ruido", monto=20.0, estado="pagada")
        db.session.add(m)
        db.session.commit()
        out, err = services.pagar_multa(m.id, casa_id)
        assert out is None and err is not None


def test_pagar_multa_de_otra_casa(app):
    with app.app_context():
        casa_id = app.config["SEED"]["casa_id"]
        otra_casa = app.config["SEED"]["casa2_id"]
        m = Multa(casa_id=casa_id, motivo="Ruido", monto=20.0, estado="pendiente")
        db.session.add(m)
        db.session.commit()
        out, err = services.pagar_multa(m.id, otra_casa)
        assert out is None and err is not None
        assert Multa.query.get(m.id).estado == "pendiente"


def test_crear_vehiculo_valida_placa(app):
    with app.app_context():
        rid = app.config["SEED"]["residente_id"]
        assert services.crear_vehiculo_residente(rid, placa="malo", marca="x",
                                                  modelo="y", color="z") is not None
        assert services.crear_vehiculo_residente(rid, placa="XYZ-4321", marca="Kia",
                                                  modelo="Rio", color="Azul") is None
        assert Vehiculo.query.filter_by(placa="XYZ-4321").first() is not None


def test_crear_vehiculo_duplicado(app):
    with app.app_context():
        rid = app.config["SEED"]["residente_id"]
        err = services.crear_vehiculo_residente(rid, placa="ABC-1234", marca="x",
                                                modelo="y", color="z")
        assert err is not None


def test_solicitar_visita_genera_pin_y_token(app):
    with app.app_context():
        casa_id = app.config["SEED"]["casa_id"]
        err = services.solicitar_visita(casa_id=casa_id, nombre_visitante="Pedro Lopez",
                                        cedula_visitante="", motivo="Familiar",
                                        placa_vehiculo="", autorizado_por="Juan")
        assert err is None
        v = Visita.query.filter_by(nombre_visitante="Pedro Lopez").first()
        assert v.pin and len(v.pin) == 6 and v.token
