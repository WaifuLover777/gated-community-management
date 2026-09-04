from datetime import datetime
from extensions import db

class Autorizado(db.Model):
    """Persona autorizada recurrente (empleada, niñera, chofer) con QR permanente."""

    __tablename__ = "autorizados"

    id = db.Column(db.Integer, primary_key=True)
    casa_id = db.Column(db.Integer, db.ForeignKey("casas.id"), nullable=False)
    residente_id = db.Column(db.Integer, db.ForeignKey("residentes.id"))
    nombre = db.Column(db.String(120), nullable=False)
    cedula = db.Column(db.String(20))
    relacion = db.Column(db.String(40))
    token = db.Column(db.String(32), unique=True, index=True, nullable=False)
    vigencia_desde = db.Column(db.Date)
    vigencia_hasta = db.Column(db.Date)
    activo = db.Column(db.Boolean, default=True)
    creado_en = db.Column(db.DateTime, default=datetime.utcnow)

    casa = db.relationship("Casa", foreign_keys=[casa_id])
    residente = db.relationship("Residente", foreign_keys=[residente_id])

    def __repr__(self):
        return f"<Autorizado {self.nombre} casa={self.casa_id}>"
