from modules.guardia import services
from models import Usuario


def _guardia_id(app):
    return Usuario.query.filter_by(rol="guardia").first().id


def test_crear_novedad_valida(app):
    with app.app_context():
        gid = _guardia_id(app)
        nov, err = services.crear_novedad(guardia_id=gid, categoria="incidente",
                                          texto="x", tipo="novedad")
        assert nov is None and err is not None
        nov, err = services.crear_novedad(guardia_id=gid, categoria="incidente",
                                          texto="Ronda sin novedad en sector A",
                                          tipo="novedad")
        assert err is None and nov is not None


def test_listar_y_actualizar(app):
    with app.app_context():
        gid = _guardia_id(app)
        nov, _ = services.crear_novedad(guardia_id=gid, categoria="general",
                                        texto="Cambio de turno 18h00", tipo="cambio_turno")
        assert len(services.listar_novedades()) == 1
        assert services.actualizar_novedad(nov.id, categoria="ronda",
                                           texto="Texto corregido") is None
