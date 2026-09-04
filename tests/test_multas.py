from modules.multas import services
from models import Multa


def test_crear_valida(app):
    with app.app_context():
        casa_id = app.config["SEED"]["casa_id"]
        assert services.crear(casa_id=casa_id, motivo="x", descripcion="", monto=0) is not None
        assert services.crear(casa_id=999, motivo="Ruido", descripcion="", monto=10) is not None
        assert services.crear(casa_id=casa_id, motivo="Ruido excesivo",
                              descripcion="fiesta", monto=25.5) is None


def test_total_pendiente_y_estado(app):
    with app.app_context():
        casa_id = app.config["SEED"]["casa_id"]
        services.crear(casa_id=casa_id, motivo="Parqueo", descripcion="", monto=15)
        total, num = services.total_pendiente_casa(casa_id)
        assert total == 15.0 and num == 1
        m = Multa.query.filter_by(casa_id=casa_id).first()
        services.cambiar_estado(m.id, "pagada")
        assert Multa.query.get(m.id).fecha_pago is not None
        assert services.total_pendiente_casa(casa_id)[0] == 0.0
