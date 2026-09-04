from functools import wraps
from flask import session, redirect, url_for, flash

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "usuario" not in session:
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated

def role_required(*roles):
    def wrapper(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if "usuario" not in session:
                return redirect(url_for("auth.login"))
            if session.get("rol") not in roles:
                flash("No tienes permiso para acceder a esa sección", "error")
                return redirect(url_for("auth.login"))
            return f(*args, **kwargs)
        return decorated
    return wrapper

admin_required = role_required("admin")
guardia_required = role_required("guardia", "admin")

def residente_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "usuario" not in session or session.get("rol") != "residente":
            return redirect(url_for("auth.login"))
        if not session.get("residente_id"):
            flash("Tu usuario no tiene un residente asociado", "error")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated
