from datetime import datetime
from extensions import db

class Reserva(db.Model):
    __tablename__ = "reservas"

    id = db.Column(db.Integer, primary_key=True)
    area_id = db.Column(db.Integer, db.ForeignKey("areas_comunes.id"), nullable=False)
    casa_id = db.Column(db.Integer, db.ForeignKey("casas.id"), nullable=False)
    residente_id = db.Column(db.Integer, db.ForeignKey("residentes.id"))
    fecha = db.Column(db.Date, nullable=False, index=True)
    hora_inicio = db.Column(db.String(5), nullable=False)
    hora_fin = db.Column(db.String(5), nullable=False)
    estado = db.Column(db.String(20), default="confirmada")
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)

    area = db.relationship("AreaComun", foreign_keys=[area_id])
    casa = db.relationship("Casa", foreign_keys=[casa_id])
    residente = db.relationship("Residente", foreign_keys=[residente_id])

    def __repr__(self):
        return f"<Reserva area={self.area_id} {self.fecha} {self.hora_inicio}-{self.hora_fin}>"
