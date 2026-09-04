from datetime import datetime
from extensions import db

class Incidencia(db.Model):
    __tablename__ = "incidencias"

    id = db.Column(db.Integer, primary_key=True)
    casa_id = db.Column(db.Integer, db.ForeignKey("casas.id"), nullable=False)
    residente_id = db.Column(db.Integer, db.ForeignKey("residentes.id"))
    titulo = db.Column(db.String(120), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    categoria = db.Column(db.String(20), default="general")
    foto = db.Column(db.String(255))
    estado = db.Column(db.String(20), default="abierto")
    respuesta = db.Column(db.Text)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.utcnow)

    casa = db.relationship("Casa", foreign_keys=[casa_id])
    residente = db.relationship("Residente", foreign_keys=[residente_id])

    def __repr__(self):
        return f"<Incidencia {self.titulo} ({self.estado})>"
