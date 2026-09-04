from flask import Blueprint, render_template
from core.decorators import admin_required
from modules.dashboard import services

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/dashboard")
@admin_required
def inicio():
    return render_template(
        "dashboard.html",
        stats=services.metricas(),
        comunicados=services.comunicados_recientes(),
        visitas=services.visitas_recientes(),
    )
