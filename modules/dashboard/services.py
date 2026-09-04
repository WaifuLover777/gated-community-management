from models import Casa, Residente, Cuota, Visita, Comunicado
from core.utils import rango_hoy_utc

def metricas():
    inicio, fin = rango_hoy_utc()
    return {
        "total_casas": Casa.query.count(),
        "total_residentes": Residente.query.filter_by(activo=True).count(),
        "cuotas_pendientes": Cuota.query.filter_by(estado="pendiente").count(),
        "cuotas_vencidas": Cuota.query.filter_by(estado="vencido").count(),
        "visitas_hoy": Visita.query.filter(
            Visita.fecha_entrada >= inicio, Visita.fecha_entrada < fin
        ).count(),
        "comunicados_activos": Comunicado.query.filter_by(activo=True).count(),
    }

def comunicados_recientes(limite=3):
    return (Comunicado.query.filter_by(activo=True)
            .order_by(Comunicado.publicado_en.desc()).limit(limite).all())

def visitas_recientes(limite=5):
    return (Visita.query.order_by(Visita.fecha_entrada.desc()).limit(limite).all())
