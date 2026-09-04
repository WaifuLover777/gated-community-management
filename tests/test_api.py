from datetime import datetime, timedelta

from extensions import db
from models import Visita


def test_buscar_placa_requiere_token(client):
    r = client.get("/api/vehiculos/buscar-placa/ABC-1234")
    assert r.status_code == 401


def test_buscar_placa_encontrada(client, api_headers):
    r = client.get("/api/vehiculos/buscar-placa/ABC-1234", headers=api_headers)
    assert r.status_code == 200
    data = r.get_json()
    assert data["encontrado"] is True
    assert data["residente"]["nombre"] == "Juan Perez"


def test_buscar_placa_no_encontrada(client, api_headers):
    r = client.get("/api/vehiculos/buscar-placa/ZZZ-9999", headers=api_headers)
    assert r.status_code == 404


def test_validar_pin_valido(client, api_headers):
    r = client.post("/api/visitas/validar-pin", json={"pin": "123456"},
                    headers=api_headers)
    assert r.status_code == 200
    assert r.get_json()["valido"] is True


def test_validar_pin_invalido(client, api_headers):
    r = client.post("/api/visitas/validar-pin", json={"pin": "000000"},
                    headers=api_headers)
    assert r.status_code == 404


def test_validar_pin_expirado(client, api_headers, app):
    with app.app_context():
        v = Visita.query.filter_by(pin="123456").first()
        v.fecha_creacion = datetime.utcnow() - timedelta(days=3)
        db.session.commit()
    r = client.post("/api/visitas/validar-pin", json={"pin": "123456"},
                    headers=api_headers)
    assert r.status_code == 404
