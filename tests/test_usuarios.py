from models import Usuario, Acceso, Novedad
from extensions import db

def test_eliminar_guardia_desvincula_registros(admin_client, app):
    with app.app_context():
        uid = Usuario.query.filter_by(email="guardia@test.com").first().id
        db.session.add(Acceso(guardia_id=uid, tipo="entrada", placa="XYZ-000"))
        db.session.add(Novedad(guardia_id=uid, texto="ronda"))
        db.session.commit()
    admin_client.get(f"/usuarios/eliminar/{uid}")
    with app.app_context():
        assert Usuario.query.get(uid) is None                       # usuario borrado
        assert Acceso.query.filter_by(guardia_id=uid).count() == 0  # FK desvinculada
        assert Novedad.query.filter_by(guardia_id=uid).count() == 0

def test_no_elimina_admin(admin_client, app):
    with app.app_context():
        uid = Usuario.query.filter_by(email="admin@test.com").first().id
    admin_client.get(f"/usuarios/eliminar/{uid}")
    with app.app_context():
        assert Usuario.query.get(uid) is not None

def test_crear_guardia(admin_client, app):
    admin_client.post("/usuarios/nuevo", data={
        "nombre":"Nuevo Guardia","email":"ng@test.com",
        "password":"clave123","rol":"guardia"})
    with app.app_context():
        assert Usuario.query.filter_by(email="ng@test.com").first() is not None


def test_residente_baja_no_puede_entrar(client, app):
    from modules.residentes import services
    with app.app_context():
        rid = app.config["SEED"]["residente_id"]
        services.dar_de_baja(rid)
    r = client.post("/login", data={"email":"residente@test.com","password":"residente123"},
                    follow_redirects=True)
    assert b"portal" not in r.request.path.encode()  # no llega al portal
    from modules.auth import services as auth
    with app.app_context():
        assert auth.autenticar("residente@test.com", "residente123") is None

def test_residente_baja_oculta_vehiculos(app):
    from modules.residentes import services
    with app.app_context():
        rid = app.config["SEED"]["residente_id"]
        assert any(v.residente_id == rid for v in services.listar_vehiculos())
        services.dar_de_baja(rid)
        assert not any(v.residente_id == rid for v in services.listar_vehiculos())
