from datetime import date, timedelta

from modules.autorizados import services
from models import Autorizado


def test_crear_valida_nombre(app):
    with app.app_context():
        casa_id = app.config["SEED"]["casa_id"]
        rid = app.config["SEED"]["residente_id"]
        assert services.crear(casa_id=casa_id, residente_id=rid, nombre="ab",
                              cedula="", relacion="empleada",
                              vigencia_desde="", vigencia_hasta="") is not None


def test_crear_rango_fechas_invalido(app):
    with app.app_context():
        casa_id = app.config["SEED"]["casa_id"]
        rid = app.config["SEED"]["residente_id"]
        hoy = date.today()
        err = services.crear(casa_id=casa_id, residente_id=rid, nombre="Maria Empleada",
                             cedula="", relacion="empleada",
                             vigencia_desde=hoy.isoformat(),
                             vigencia_hasta=(hoy - timedelta(days=1)).isoformat())
        assert err is not None


def test_crear_y_alternar(app):
    with app.app_context():
        casa_id = app.config["SEED"]["casa_id"]
        rid = app.config["SEED"]["residente_id"]
        assert services.crear(casa_id=casa_id, residente_id=rid, nombre="Chofer Diario",
                              cedula="", relacion="chofer",
                              vigencia_desde="", vigencia_hasta="") is None
        a = Autorizado.query.first()
        assert a.activo and a.token
        services.alternar(a.id, casa_id)
        assert Autorizado.query.get(a.id).activo is False
