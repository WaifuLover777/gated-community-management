from core.reconocimiento import qr
from modules.garita import services
from models import Visita


def test_qr_visita_roundtrip_y_validacion(app):
    with app.app_context():
        v = Visita.query.filter_by(pin="123456").first()
        v.token = "tok-de-prueba-123"
        from extensions import db
        db.session.commit()
        png = qr.png_visita(v.token)
        assert qr.leer_qr(png) == qr.PREFIJO_VISITA + v.token
        res = services.validar_qr(qr.PREFIJO_VISITA + v.token)
        assert res["ok"] is True
        assert services.validar_qr(qr.PREFIJO_VISITA + v.token)["ok"] is False


def test_qr_residente_firma_valida(app):
    with app.app_context():
        rid = app.config["SEED"]["residente_id"]
        firma = qr.firmar_residente(rid)
        assert qr.verificar_residente(firma) == rid
        res = services.validar_qr(qr.PREFIJO_RESIDENTE + firma)
        assert res["ok"] is True


def test_qr_invalido(app):
    with app.app_context():
        assert services.validar_qr("texto cualquiera")["ok"] is False
        assert services.validar_qr("")["ok"] is False


def test_control_station_requiere_guardia(client):
    r = client.get("/guardia/control")
    assert r.status_code == 302


def test_api_qr_validar_con_contenido(client, api_headers, app):
    with app.app_context():
        rid = app.config["SEED"]["residente_id"]
        firma = qr.firmar_residente(rid)
    r = client.post("/api/qr/validar",
                    json={"contenido": qr.PREFIJO_RESIDENTE + firma},
                    headers=api_headers)
    assert r.status_code == 200
    assert r.get_json()["ok"] is True
