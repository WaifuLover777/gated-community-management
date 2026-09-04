from modules.dashboard import services


def test_metricas_estructura_y_conteos(app):
    with app.app_context():
        m = services.metricas()
        assert m["total_casas"] == 2
        assert m["total_residentes"] == 1
        assert m["cuotas_pendientes"] >= 1
        assert m["cuotas_vencidas"] >= 1
        assert set(m) >= {"total_casas", "total_residentes", "cuotas_pendientes",
                          "cuotas_vencidas", "visitas_hoy", "comunicados_activos"}
