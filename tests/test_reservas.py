from datetime import date, timedelta

from modules.reservas import services


def _crear_area(app):
    services.crear_area(nombre="Salon", descripcion="",
                        hora_apertura="08:00", hora_cierre="22:00")
    from models import AreaComun
    return AreaComun.query.first().id


def test_overlap_rechaza_segunda(app):
    with app.app_context():
        aid = _crear_area(app)
        casa_id = app.config["SEED"]["casa_id"]
        f = (date.today() + timedelta(days=1)).isoformat()
        assert services.crear_reserva(area_id=aid, casa_id=casa_id, residente_id=None,
                                       fecha=f, hora_inicio="10:00", hora_fin="12:00") is None
        err = services.crear_reserva(area_id=aid, casa_id=casa_id, residente_id=None,
                                     fecha=f, hora_inicio="11:00", hora_fin="13:00")
        assert err is not None


def test_contigua_se_acepta(app):
    with app.app_context():
        aid = _crear_area(app)
        casa_id = app.config["SEED"]["casa_id"]
        f = (date.today() + timedelta(days=1)).isoformat()
        services.crear_reserva(area_id=aid, casa_id=casa_id, residente_id=None,
                               fecha=f, hora_inicio="10:00", hora_fin="12:00")
        assert services.crear_reserva(area_id=aid, casa_id=casa_id, residente_id=None,
                                      fecha=f, hora_inicio="12:00", hora_fin="14:00") is None


def test_fecha_pasada_rechaza(app):
    with app.app_context():
        aid = _crear_area(app)
        casa_id = app.config["SEED"]["casa_id"]
        ayer = (date.today() - timedelta(days=1)).isoformat()
        err = services.crear_reserva(area_id=aid, casa_id=casa_id, residente_id=None,
                                     fecha=ayer, hora_inicio="10:00", hora_fin="11:00")
        assert err is not None
