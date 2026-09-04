from modules.paqueteria import services
from models import Paquete, Notificacion


def test_registrar_notifica_y_entregar(app):
    with app.app_context():
        casa_id = app.config["SEED"]["casa_id"]
        rid = app.config["SEED"]["residente_id"]
        err = services.registrar(casa_id=casa_id, descripcion="Caja Amazon",
                                 remitente="Amazon", recibido_por="Guardia")
        assert err is None
        p = Paquete.query.first()
        assert p.estado == "recibido"
        assert Notificacion.query.filter_by(residente_id=rid).count() >= 1
        services.marcar_entregado(p.id, retirado_por="Maria")
        p = Paquete.query.get(p.id)
        assert p.estado == "entregado" and p.retirado_por == "Maria"


def test_registrar_casa_invalida(app):
    with app.app_context():
        assert services.registrar(casa_id=999, descripcion="x", remitente="",
                                  recibido_por="G") is not None
