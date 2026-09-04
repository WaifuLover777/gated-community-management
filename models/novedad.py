from datetime import datetime
from extensions import db

class Novedad(db.Model):
    __tablename__ = "novedades"

    id = db.Column(db.Integer, primary_key=True)
    fecha_hora = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    categoria = db.Column(db.String(20), default="general")
    texto = db.Column(db.Text, nullable=False)
    foto = db.Column(db.String(255))
    tipo = db.Column(db.String(20), default="novedad")

    guardia_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"))
    guardia = db.relationship("Usuario", foreign_keys=[guardia_id])

    def __repr__(self):
        return f"<Novedad {self.categoria} {self.fecha_hora}>"
