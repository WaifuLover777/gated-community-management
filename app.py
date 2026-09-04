import secrets

from flask import Flask, redirect, url_for, session
from config import Config
from extensions import db, migrate, csrf, limiter
from core.utils import fmt_dt

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    if not app.config.get("SECRET_KEY"):
        if app.config.get("DEBUG"):
            app.config["SECRET_KEY"] = secrets.token_hex(32)
        else:
            raise RuntimeError(
                "SECRET_KEY no configurada. Define la variable de entorno "
                "SECRET_KEY antes de arrancar en producción."
            )

    db.init_app(app)

    migrate.init_app(app, db, render_as_batch=True)
    csrf.init_app(app)
    limiter.init_app(app)

    from models import (
        Usuario, Casa, Residente, Vehiculo, Cuota, Visita, Comunicado, Acceso,
    )

    app.jinja_env.filters["dt"] = fmt_dt

    @app.context_processor
    def _inyectar_notificaciones():
        from flask import session
        rid = session.get("residente_id")
        if not rid or session.get("rol") != "residente":
            return {}
        from core import notificaciones
        return {"notif_no_leidas": notificaciones.contar_no_leidas(rid)}

    _registrar_blueprints(app)
    _registrar_cli(app)

    @app.route("/")
    def index():
        if "usuario" in session:
            rol = session.get("rol")
            destino = {"admin": "dashboard.inicio", "guardia": "guardia.inicio",
                       "residente": "portal.inicio"}.get(rol)
            if destino:
                return redirect(url_for(destino))
        return redirect(url_for("auth.login"))

    return app

def _registrar_blueprints(app):
    from modules.auth.routes import auth_bp
    from modules.dashboard.routes import dashboard_bp
    from modules.residentes.routes import residentes_bp
    from modules.pagos.routes import pagos_bp
    from modules.visitas.routes import visitas_bp
    from modules.comunicados.routes import comunicados_bp
    from modules.portal.routes import portal_bp
    from modules.guardia.routes import guardia_bp
    from modules.usuarios.routes import usuarios_bp
    from modules.accesos.routes import accesos_bp
    from modules.incidencias.routes import incidencias_bp
    from modules.reservas.routes import reservas_bp
    from modules.multas.routes import multas_bp
    from modules.paqueteria.routes import paqueteria_bp
    from modules.garita.routes import garita_bp
    from modules.autorizados.routes import autorizados_bp
    from api import api_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(residentes_bp, url_prefix="/residentes")
    app.register_blueprint(pagos_bp, url_prefix="/pagos")
    app.register_blueprint(visitas_bp, url_prefix="/visitas")
    app.register_blueprint(comunicados_bp, url_prefix="/comunicados")
    app.register_blueprint(portal_bp)
    app.register_blueprint(guardia_bp)
    app.register_blueprint(usuarios_bp)
    app.register_blueprint(accesos_bp)
    app.register_blueprint(incidencias_bp)
    app.register_blueprint(reservas_bp)
    app.register_blueprint(multas_bp)
    app.register_blueprint(paqueteria_bp)
    app.register_blueprint(garita_bp)
    app.register_blueprint(autorizados_bp)
    app.register_blueprint(api_bp)

    csrf.exempt(api_bp)

def _registrar_cli(app):
    @app.cli.command("seed")
    def seed():
        from seeds import seed_datos
        seed_datos()
        print("Datos de prueba cargados.")

    @app.cli.command("purgar-evidencia")
    def purgar_evidencia():
        """Borra fotos de evidencia de accesos según la política de retención."""
        from modules.garita import services
        n = services.purgar_evidencia()
        print(f"Evidencia purgada: {n} registro(s).")

app = create_app()

if __name__ == "__main__":
    app.run(debug=app.config.get("DEBUG", False))
