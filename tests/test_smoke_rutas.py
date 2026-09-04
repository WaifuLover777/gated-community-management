"""Red de regresión ancha: ninguna página GET debe devolver 5xx."""
from models import Visita, Vehiculo


def _rutas_get(app):
    rutas = set()
    for rule in app.url_map.iter_rules():
        if "GET" not in rule.methods:
            continue
        if rule.arguments:
            continue
        if rule.endpoint == "static" or rule.rule == "/logout":
            continue
        rutas.add(rule.rule)
    return sorted(rutas)


def _smoke(client, app):
    fallos = []
    for ruta in _rutas_get(app):
        resp = client.get(ruta)
        if resp.status_code >= 500:
            fallos.append((ruta, resp.status_code))
    return fallos


def test_smoke_anonimo(client, app):
    assert _smoke(client, app) == []


def test_smoke_residente(residente_client, app):
    assert _smoke(residente_client, app) == []


def test_smoke_guardia(guardia_client, app):
    assert _smoke(guardia_client, app) == []


def test_smoke_admin(admin_client, app):
    assert _smoke(admin_client, app) == []


def test_rutas_parametricas_residente(residente_client, app):
    """Rutas GET con <id> usando ids reales del seed: no deben dar 5xx."""
    with app.app_context():
        vid = Visita.query.first().id
        veh = Vehiculo.query.first().id
    objetivo = [
        "/portal/qr",
        f"/portal/visitas/{vid}/qr",
        f"/portal/vehiculos/{veh}/editar",
    ]
    for ruta in objetivo:
        assert residente_client.get(ruta).status_code < 500, ruta


def test_rutas_parametricas_guardia(guardia_client, app):
    for cam in ("frontal", "trasera", "cabina"):
        assert guardia_client.get(f"/guardia/control/snapshot/{cam}").status_code < 500
