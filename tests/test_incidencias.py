from modules.incidencias import services
from models import Incidencia


def test_crear_valida(app):
    with app.app_context():
        casa_id = app.config["SEED"]["casa_id"]
        rid = app.config["SEED"]["residente_id"]
        assert services.crear(casa_id=casa_id, residente_id=rid, titulo="ab",
                              descripcion="x", categoria="plomeria") is not None
        assert services.crear(casa_id=casa_id, residente_id=rid, titulo="Fuga de agua",
                              descripcion="Hay una fuga en la acera",
                              categoria="plomeria") is None


def test_flujo_estado_y_respuesta(app):
    with app.app_context():
        casa_id = app.config["SEED"]["casa_id"]
        rid = app.config["SEED"]["residente_id"]
        services.crear(casa_id=casa_id, residente_id=rid, titulo="Luz dañada",
                       descripcion="El poste no enciende", categoria="electricidad")
        i = Incidencia.query.first()
        assert i.estado == "abierto"
        err = services.actualizar_estado(i.id, estado="en_proceso",
                                         respuesta="Enviamos técnico")
        assert err is None
        i = Incidencia.query.get(i.id)
        assert i.estado == "en_proceso" and i.respuesta == "Enviamos técnico"
        assert services.actualizar_estado(i.id, estado="zzz") is not None


def test_listar_de_casa(app):
    with app.app_context():
        casa_id = app.config["SEED"]["casa_id"]
        rid = app.config["SEED"]["residente_id"]
        services.crear(casa_id=casa_id, residente_id=rid, titulo="Tema uno",
                       descripcion="Descripción válida", categoria="general")
        assert len(services.listar_de_casa(casa_id)) == 1
