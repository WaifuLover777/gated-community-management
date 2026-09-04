import os
import tempfile
from datetime import date

import pytest

from config import Config
from app import create_app
from extensions import db as _db


def _make_config(ratelimit=False):
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)

    class TestConfig(Config):
        TESTING = True
        WTF_CSRF_ENABLED = False
        SECRET_KEY = "test-secret"
        API_TOKEN = "test-token"
        NOTIF_BACKEND = "consola"
        RECOG_ROSTRO_BACKEND = "sim"
        RECOG_PLACA_BACKEND = "sim"
        SQLALCHEMY_DATABASE_URI = "sqlite:///" + path
        RATELIMIT_ENABLED = ratelimit

    TestConfig._path = path
    return TestConfig


def _seed():
    from models import Usuario, Casa, Residente, Vehiculo, Visita, Cuota
    hoy = date.today()

    casa = Casa(numero="A-01", manzana="A", alicuota=45.0, capacidad=5)
    casa2 = Casa(numero="B-02", manzana="B", alicuota=50.0, capacidad=5,
                 pin_registro="654321")
    _db.session.add_all([casa, casa2])
    _db.session.flush()

    guardia = Usuario(nombre="Guardia", email="guardia@test.com", rol="guardia")
    guardia.set_password("guardia123")
    admin = Usuario(nombre="Admin", email="admin@test.com", rol="admin")
    admin.set_password("admin123")
    _db.session.add_all([guardia, admin])

    res = Residente(casa_id=casa.id, nombre="Juan Perez", cedula="0999999999",
                    email="res@test.com", tipo="propietario")
    _db.session.add(res)
    _db.session.flush()

    u_res = Usuario(nombre=res.nombre, email="residente@test.com",
                    rol="residente", residente_id=res.id)
    u_res.set_password("residente123")
    _db.session.add(u_res)

    _db.session.add(Vehiculo(residente_id=res.id, placa="ABC-1234",
                             marca="Toyota", modelo="Yaris", color="Rojo"))
    _db.session.add(Visita(casa_id=casa.id, nombre_visitante="Visitante Uno",
                           estado="pendiente", pin="123456", token="tok-seed-1"))

    _db.session.add_all([
        Cuota(casa_id=casa.id, mes=hoy.month, anio=hoy.year, monto=45.0,
              estado="pendiente", concepto=""),
        Cuota(casa_id=casa.id, mes=1, anio=2024, monto=45.0, estado="vencido", concepto=""),
        Cuota(casa_id=casa.id, mes=2, anio=2024, monto=45.0, estado="pagado",
              concepto="", fecha_pago="2024-02-10", metodo_pago="efectivo"),
        Cuota(casa_id=casa.id, mes=3, anio=2024, monto=45.0, estado="en_revision",
              concepto="", metodo_pago="transferencia"),
    ])
    _db.session.commit()
    return {
        "casa_id": casa.id, "casa2_id": casa2.id, "residente_id": res.id,
        "pin_casa2": "654321",
    }


@pytest.fixture
def app():
    cfg = _make_config(ratelimit=False)
    app = create_app(cfg)
    with app.app_context():
        _db.create_all()
        app.config["SEED"] = _seed()
        yield app
        _db.session.remove()
        _db.drop_all()
    try:
        os.remove(cfg._path)
    except OSError:
        pass


def login(client, email, password):
    return client.post("/login", data={"email": email, "password": password})


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def admin_client(app):
    c = app.test_client()
    login(c, "admin@test.com", "admin123")
    return c


@pytest.fixture
def guardia_client(app):
    c = app.test_client()
    login(c, "guardia@test.com", "guardia123")
    return c


@pytest.fixture
def residente_client(app):
    c = app.test_client()
    login(c, "residente@test.com", "residente123")
    return c


@pytest.fixture
def api_headers():
    return {"X-API-Key": "test-token"}
