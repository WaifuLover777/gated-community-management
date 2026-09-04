from modules.auth import services
from models import Usuario, Residente


def _registro(pin, cedula="0911111111", email="nuevo@test.com"):
    return services.registrar_residente(
        nombre="Nuevo Residente", cedula=cedula, telefono="0999999999",
        email=email, password="clave123", pin=pin, tipo="propietario")


def test_registro_pin_invalido(app):
    with app.app_context():
        usuario, err = _registro("000000")
        assert usuario is None and err is not None


def test_registro_exitoso_y_pin_un_solo_uso(app):
    with app.app_context():
        pin = app.config["SEED"]["pin_casa2"]
        usuario, err = _registro(pin)
        assert err is None and usuario is not None
        assert Residente.query.filter_by(email="nuevo@test.com").first() is not None
        u2, err2 = _registro(pin, cedula="0922222222", email="otro@test.com")
        assert u2 is None and err2 is not None


def test_registro_cedula_duplicada(app):
    with app.app_context():
        pin = app.config["SEED"]["pin_casa2"]
        usuario, err = _registro(pin, cedula="0999999999", email="x@test.com")
        assert usuario is None and err is not None
