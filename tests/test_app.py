import models
from extensions import db


def test_app_arranca_con_blueprints(app):
    rutas = list(app.url_map.iter_rules())
    assert len(rutas) > 60
    blueprints = set(app.blueprints)
    esperados = {"auth", "dashboard", "portal", "guardia", "pagos", "visitas",
                 "comunicados", "residentes", "usuarios", "accesos", "incidencias",
                 "reservas", "multas", "paqueteria", "garita", "autorizados", "api"}
    assert esperados <= blueprints


def test_modelos_tienen_tabla(app):
    with app.app_context():
        tablas = set(db.metadata.tables)
        for nombre in models.__all__:
            modelo = getattr(models, nombre)
            assert modelo.__tablename__ in tablas, nombre


def test_index_redirige(client):
    r = client.get("/")
    assert r.status_code in (301, 302)
