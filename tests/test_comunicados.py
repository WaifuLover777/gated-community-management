from modules.comunicados import services
from models import Comunicado, Notificacion


def test_crear_invalido(app):
    with app.app_context():
        assert services.crear(titulo="ab", contenido="x", tipo="anuncio",
                              publicado_por="Admin") is not None


def test_crear_publicado_notifica(app):
    with app.app_context():
        err = services.crear(titulo="Corte de agua", contenido="Mañana de 8 a 12",
                             tipo="urgente", publicado_por="Admin")
        assert err is None
        assert Comunicado.query.filter_by(titulo="Corte de agua").first() is not None
        assert Notificacion.query.filter_by(tipo="comunicado").count() >= 1


def test_archivar(app):
    with app.app_context():
        services.crear(titulo="Aviso temporal", contenido="contenido valido",
                       tipo="anuncio", publicado_por="Admin")
        c = Comunicado.query.filter_by(titulo="Aviso temporal").first()
        services.archivar(c.id)
        assert Comunicado.query.get(c.id).activo is False
