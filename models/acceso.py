from datetime import datetime
from extensions import db

class Acceso(db.Model):
    __tablename__ = "accesos"

    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(20))
    fecha_hora = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    resultado = db.Column(db.String(20))
    observacion = db.Column(db.Text)
    placa = db.Column(db.String(15))
    placa_frontal = db.Column(db.String(15))
    placa_trasera = db.Column(db.String(15))
    metodo = db.Column(db.String(20))
    confianza = db.Column(db.Float)
    foto_evidencia = db.Column(db.String(255))

    guardia_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"))
    residente_id = db.Column(db.Integer, db.ForeignKey("residentes.id"))
    visita_id = db.Column(db.Integer, db.ForeignKey("visitas.id"))

    guardia = db.relationship("Usuario", foreign_keys=[guardia_id])
    residente = db.relationship("Residente", foreign_keys=[residente_id])
    visita = db.relationship("Visita", foreign_keys=[visita_id])

    def __repr__(self):
        return f"<Acceso {self.tipo} {self.resultado} {self.fecha_hora}>"
