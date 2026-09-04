from datetime import datetime
from extensions import db

class ListaNegra(db.Model):
    """Placas vetadas: ingreso denegado automáticamente con alerta al guardia."""

    id = db.Column(db.Integer, primary_key=True)
    placa = db.Column(db.String(15), unique=True, index=True, nullable=False)
    motivo = db.Column(db.String(200))
    activo = db.Column(db.Boolean, default=True)
    creado_en = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<ListaNegra {self.placa} activo={self.activo}>"
