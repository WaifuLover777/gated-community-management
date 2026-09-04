from datetime import datetime
from extensions import db

class RostroEnrolado(db.Model):
    """Rostro enrolado (embedding) de un residente o visitante."""

    __tablename__ = "rostros"

    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(20), default="residente")
    residente_id = db.Column(db.Integer, db.ForeignKey("residentes.id"), index=True)
    embedding = db.Column(db.Text, nullable=False)
    foto = db.Column(db.String(255))
    consentimiento = db.Column(db.Boolean, default=False)
    creado_en = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    residente = db.relationship("Residente", foreign_keys=[residente_id])

    def __repr__(self):
        return f"<RostroEnrolado {self.tipo} res={self.residente_id}>"
