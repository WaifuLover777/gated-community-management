from datetime import datetime
from extensions import db

class Paquete(db.Model):
    __tablename__ = "paquetes"

    id = db.Column(db.Integer, primary_key=True)
    casa_id = db.Column(db.Integer, db.ForeignKey("casas.id"), nullable=False)
    descripcion = db.Column(db.String(200), nullable=False)
    remitente = db.Column(db.String(120))
    foto = db.Column(db.String(255))
    estado = db.Column(db.String(20), default="recibido")
    recibido_por = db.Column(db.String(120))
    retirado_por = db.Column(db.String(120))
    creado_en = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    fecha_entrega = db.Column(db.DateTime)

    casa = db.relationship("Casa", foreign_keys=[casa_id])

    def __repr__(self):
        return f"<Paquete casa={self.casa_id} {self.estado}>"
