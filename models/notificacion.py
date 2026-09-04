from datetime import datetime
from extensions import db

class Notificacion(db.Model):
    __tablename__ = "notificaciones"

    id = db.Column(db.Integer, primary_key=True)
    residente_id = db.Column(db.Integer, db.ForeignKey("residentes.id"), index=True)
    titulo = db.Column(db.String(120), nullable=False)
    mensaje = db.Column(db.Text, nullable=False)
    tipo = db.Column(db.String(20), default="info")
    leido = db.Column(db.Boolean, default=False)
    creado_en = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def __repr__(self):
        return f"<Notificacion res={self.residente_id} {self.tipo} leido={self.leido}>"
