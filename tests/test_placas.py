from core.reconocimiento import placas
from modules.garita import services
from models import Cuota
from extensions import db


def _poner_al_dia(casa_id):
    Cuota.query.filter_by(casa_id=casa_id).update({"estado": "pagado"})
    db.session.commit()


def test_sim_lee_placa_de_nombre(app):
    with app.app_context():
        assert placas.leer_placa(b"", pista="ABC-1234.jpg")["placa"] == "ABC-1234"
        assert placas.leer_placa(b"", pista="foto_XYZ9876_frontal.png")["placa"] == "XYZ-9876"
        assert placas.leer_placa(b"", pista="sin_placa.jpg") is None


def test_entrada_al_dia_autoriza(app):
    with app.app_context():
        _poner_al_dia(app.config["SEED"]["casa_id"])
        r = services.procesar_placas(placa_frontal="ABC-1234", placa_trasera="ABC-1234")
        assert r["ok"] is True
        assert r["estado_financiero"] == "al_dia"


def test_anti_passback(app):
    with app.app_context():
        _poner_al_dia(app.config["SEED"]["casa_id"])
        services.procesar_placas(placa_frontal="ABC-1234", placa_trasera="ABC-1234")
        r2 = services.procesar_placas(placa_frontal="ABC-1234", placa_trasera="ABC-1234")
        assert r2["ok"] is False
        assert "dentro" in r2["mensaje"]


def test_moroso_denegado(app):
    with app.app_context():
        casa_id = app.config["SEED"]["casa_id"]
        db.session.add(Cuota(casa_id=casa_id, mes=1, anio=2026, monto=45.0,
                             estado="vencido", concepto="alicuota"))
        db.session.commit()
        r = services.procesar_placas(placa_frontal="ABC-1234", placa_trasera="ABC-1234")
        assert r["ok"] is False


def test_lista_negra(app):
    with app.app_context():
        services.agregar_lista_negra("XXX-0000", "prueba")
        r = services.procesar_placas(placa_frontal="XXX-0000", placa_trasera="XXX-0000")
        assert r["ok"] is False
        assert r.get("alerta") is True


def test_discrepancia_frontal_trasera(app):
    with app.app_context():
        r = services.procesar_placas(placa_frontal="ABC-1234", placa_trasera="ZZZ-9999")
        assert r.get("discrepancia") is True
