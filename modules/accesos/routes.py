from flask import Blueprint, render_template
from core.decorators import admin_required
from modules.accesos import services

accesos_bp = Blueprint("accesos", __name__)

@accesos_bp.route("/accesos")
@admin_required
def lista():
    return render_template("accesos.html", accesos=services.listar())
