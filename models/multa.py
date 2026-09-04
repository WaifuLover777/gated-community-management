from datetime import datetime, date
from extensions import db

class Multa(db.Model):
    __tablename__ = "multas"

    id = db.Column(db.Integer, primary_key=True)
    casa_id = db.Column(db.Integer, db.ForeignKey("casas.id"), nullable=False)
    motivo = db.Column(db.String(120), nullable=False)
    descripcion = db.Column(db.Text)
    monto = db.Column(db.Float, nullable=False)
    estado = db.Column(db.String(20), default="pendiente")
    fecha = db.Column(db.Date, default=date.today)
    fecha_pago = db.Column(db.String(20))
    creado_en = db.Column(db.DateTime, default=datetime.utcnow)

    casa = db.relationship("Casa", foreign_keys=[casa_id])

    def __repr__(self):
        return f"<Multa casa={self.casa_id} ${self.monto} {self.estado}>"
