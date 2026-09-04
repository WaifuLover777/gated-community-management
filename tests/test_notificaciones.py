from core import notificaciones
from models import Notificacion


def test_notificar_residente_y_bandeja(app):
    with app.app_context():
        rid = app.config["SEED"]["residente_id"]
        notificaciones.notificar_residente(rid, "Hola", "mensaje de prueba", tipo="info")
        assert notificaciones.contar_no_leidas(rid) == 1
        assert len(notificaciones.bandeja(rid)) == 1
        notificaciones.marcar_leidas(rid)
        assert notificaciones.contar_no_leidas(rid) == 0


def test_notificar_casa(app):
    with app.app_context():
        casa_id = app.config["SEED"]["casa_id"]
        n = notificaciones.notificar_casa(casa_id, "Aviso", "para toda la casa")
        assert n >= 1
        assert Notificacion.query.count() >= 1


def test_notificar_todos(app):
    with app.app_context():
        n = notificaciones.notificar_todos("General", "a todos")
        assert n >= 1
