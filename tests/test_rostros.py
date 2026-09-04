import numpy as np
import cv2

from modules.garita import services
from models import Acceso
from extensions import db


def _jpg(seed):
    rng = np.random.default_rng(seed)
    img = rng.integers(0, 255, (160, 160, 3)).astype("uint8")
    return cv2.imencode(".jpg", img)[1].tobytes()


def test_enrolar_requiere_consentimiento(app):
    with app.app_context():
        rid = app.config["SEED"]["residente_id"]
        assert services.enrolar_rostro(_jpg(1), rid, consentimiento=False) is not None
        assert services.enrolar_rostro(_jpg(1), rid, consentimiento=True) is None


def test_identifica_enrolado_y_desconocido(app):
    with app.app_context():
        rid = app.config["SEED"]["residente_id"]
        img = _jpg(1)
        services.enrolar_rostro(img, rid, consentimiento=True)
        r = services.procesar_rostros(img)
        assert r["ok"] is True
        r2 = services.procesar_rostros(_jpg(2))
        assert r2["ok"] is False
        assert r2.get("alerta") is True


def test_purga_evidencia(app):
    from datetime import datetime, timedelta
    with app.app_context():
        rid = app.config["SEED"]["residente_id"]
        services.enrolar_rostro(_jpg(1), rid, consentimiento=True)
        services.procesar_rostros(_jpg(1))
        Acceso.query.update({"fecha_hora": datetime.utcnow() - timedelta(days=400)})
        db.session.commit()
        assert services.purgar_evidencia(dias=30) >= 1


def test_baja_borra_rostro_y_no_reconoce(app):
    from modules.residentes import services as res_srv
    from models import RostroEnrolado
    with app.app_context():
        rid = app.config["SEED"]["residente_id"]
        img = _jpg(1)
        services.enrolar_rostro(img, rid, consentimiento=True)
        res_srv.dar_de_baja(rid)
        assert RostroEnrolado.query.filter_by(residente_id=rid).count() == 0  # biométrico borrado
        assert services.procesar_rostros(img)["ok"] is False                 # ya no lo reconoce


def test_baja_bloquea_placa_y_autorizado(app):
    from modules.residentes import services as res_srv
    from models import Vehiculo, Autorizado, Residente
    with app.app_context():
        rid = app.config["SEED"]["residente_id"]
        casa_id = app.config["SEED"]["casa_id"]
        db.session.add(Autorizado(casa_id=casa_id, residente_id=rid, nombre="Nana",
                                  token="tok-aut-1", activo=True))
        db.session.commit()
        placa = Vehiculo.query.filter_by(residente_id=rid).first().placa
        res_srv.dar_de_baja(rid)
        # placa del residente dado de baja: no la reconoce como residente
        r = services.procesar_placas(placa_frontal=placa, placa_trasera=None)
        assert r.get("residente") is None
        # autorizado de un residente dado de baja: denegado
        a = services._validar_autorizado("tok-aut-1", guardia_id=None)
        assert a["ok"] is False
