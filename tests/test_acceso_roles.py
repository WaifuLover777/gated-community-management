"""Control de acceso por rol de las páginas de las features administrativas."""
import pytest

MATRIZ = [
    ("/portal/incidencias", {"residente"}),
    ("/incidencias", {"admin"}),
    ("/portal/reservas", {"residente"}),
    ("/areas", {"admin"}),
    ("/multas", {"admin"}),
    ("/guardia/paqueteria", {"guardia", "admin"}),
    ("/portal/paqueteria", {"residente"}),
    ("/guardia/novedades", {"guardia", "admin"}),
    ("/portal/notificaciones", {"residente"}),
    ("/comunicados/", {"admin", "guardia", "residente"}),
]


@pytest.fixture
def clientes(client, admin_client, guardia_client, residente_client):
    return {
        "anon": client,
        "admin": admin_client,
        "guardia": guardia_client,
        "residente": residente_client,
    }


@pytest.mark.parametrize("ruta,permitidos", MATRIZ)
def test_acceso_por_rol(clientes, ruta, permitidos):
    for rol, cli in clientes.items():
        resp = cli.get(ruta)
        if rol in permitidos:
            assert resp.status_code == 200, f"{rol} debería VER {ruta} (got {resp.status_code})"
        else:
            assert resp.status_code == 302, f"{rol} debería estar BLOQUEADO en {ruta} (got {resp.status_code})"


MATRIZ_POST = [
    ("/portal/incidencias/nueva", {"residente"}),
    ("/incidencias/999999/estado", {"admin"}),
    ("/portal/reservas/nueva", {"residente"}),
    ("/portal/reservas/999999/cancelar", {"residente"}),
    ("/areas/nueva", {"admin"}),
    ("/areas/999999/alternar", {"admin"}),
    ("/multas/nueva", {"admin"}),
    ("/multas/999999/estado", {"admin"}),
    ("/guardia/paqueteria/nuevo", {"guardia", "admin"}),
    ("/guardia/paqueteria/999999/entregar", {"guardia", "admin"}),
    ("/comunicados/nuevo", {"admin"}),
    ("/comunicados/editar/999999", {"admin"}),
    ("/guardia/visitas/autorizar/999999", {"guardia", "admin"}),
    ("/guardia/novedades/nueva", {"guardia", "admin"}),
    ("/guardia/novedades/999999/editar", {"guardia", "admin"}),
]


def _redirige_a_login(resp):
    return resp.status_code == 302 and "/login" in resp.headers.get("Location", "")


@pytest.mark.parametrize("ruta,permitidos", MATRIZ_POST)
def test_acceso_post_por_rol(clientes, ruta, permitidos):
    for rol, cli in clientes.items():
        if rol in permitidos:
            continue
        resp = cli.post(ruta, data={})
        assert _redirige_a_login(resp), f"{rol} NO fue bloqueado en POST {ruta} (got {resp.status_code})"
