from datetime import datetime
from extensions import db

class Visita(db.Model):
    __tablename__ = "visitas"

    id = db.Column(db.Integer, primary_key=True)
    casa_id = db.Column(db.Integer, db.ForeignKey("casas.id"), nullable=False)
    nombre_visitante = db.Column(db.String(120), nullable=False)
    cedula_visitante = db.Column(db.String(20))
    motivo = db.Column(db.String(200))
    placa_vehiculo = db.Column(db.String(15))
    pin = db.Column(db.String(6), index=True)
    token = db.Column(db.String(32), unique=True, index=True)
    estado = db.Column(db.String(20), default="pendiente")
    autorizado_por = db.Column(db.String(120))
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_entrada = db.Column(db.DateTime)
    fecha_salida = db.Column(db.DateTime)

    def __repr__(self):
        return f"<Visita {self.nombre_visitante} PIN={self.pin} {self.estado}>"
