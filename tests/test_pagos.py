from datetime import date

from modules.pagos import services
from models import Cuota, Casa
from extensions import db


class _Cuota:
    """Cuota ligera en memoria para probar cálculos puros."""
    def __init__(self, monto, mes, anio, estado="pendiente", recargo=0):
        self.monto, self.mes, self.anio = monto, mes, anio
        self.estado, self.recargo = estado, recargo


def test_meses_atraso():
    assert services.meses_atraso(_Cuota(45, 1, 2024), hoy=date(2024, 4, 1)) == 3
    assert services.meses_atraso(_Cuota(45, 6, 2024), hoy=date(2024, 4, 1)) == 0


def test_calcular_recargo_vencido(app):
    with app.app_context():
        c = _Cuota(100, 1, 2024, estado="vencido")
        assert services.calcular_recargo(c, hoy=date(2024, 4, 1)) == 30.0


def test_calcular_recargo_pagado_no_aplica(app):
    with app.app_context():
        c = _Cuota(100, 1, 2024, estado="pagado", recargo=5)
        assert services.calcular_recargo(c, hoy=date(2024, 4, 1)) == 5.0


def test_total_con_recargo(app):
    with app.app_context():
        c = _Cuota(100, 1, 2024, estado="vencido")
        assert services.total_con_recargo(c, hoy=date(2024, 4, 1)) == 130.0


def test_marcar_vencidas_auto(app):
    with app.app_context():
        casa_id = app.config["SEED"]["casa_id"]
        db.session.add(Cuota(casa_id=casa_id, mes=1, anio=2020, monto=45,
                             estado="pendiente", concepto="x"))
        db.session.commit()
        n = services.marcar_vencidas_auto()
        assert n >= 1
        assert Cuota.query.filter_by(anio=2020, concepto="x").first().estado == "vencido"


def test_generar_rechaza_pasado(app):
    with app.app_context():
        n, err = services.generar(1, 2020)
        assert n == 0 and err is not None


def test_generar_no_duplica(app):
    with app.app_context():
        hoy = date.today()
        anio = hoy.year + 1
        n1, _ = services.generar(hoy.month, anio)
        n2, _ = services.generar(hoy.month, anio)
        assert n1 == Casa.query.count()
        assert n2 == 0


def test_generar_extraordinaria_valida(app):
    with app.app_context():
        assert services.generar_extraordinaria(concepto="", monto=10,
                                               anio=date.today().year + 1, mes=1)[1]
        assert services.generar_extraordinaria(concepto="Piscina", monto=-5,
                                               anio=date.today().year + 1, mes=1)[1]
        n, err = services.generar_extraordinaria(concepto="Piscina", monto=25,
                                                 anio=date.today().year + 1, mes=1)
        assert err is None and n == Casa.query.count()


def test_confirmar_y_rechazar_transferencia(app):
    with app.app_context():
        casa_id = app.config["SEED"]["casa_id"]
        cu = Cuota.query.filter_by(casa_id=casa_id, estado="en_revision").first()
        ok, err = services.confirmar_transferencia(cu.id)
        assert err is None and ok.estado == "pagado"
        assert services.rechazar_transferencia(cu.id)[1] is not None


def test_reporte_cobranza_estructura(app):
    with app.app_context():
        rep = services.reporte_cobranza(2024)
        assert {"esperado", "cobrado", "porcentaje_recaudacion", "morosos"} <= set(rep)
        assert isinstance(rep["morosos"], list)
