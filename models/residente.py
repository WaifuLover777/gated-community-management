from datetime import date
from extensions import db

class Residente(db.Model):
    __tablename__ = "residentes"

    id = db.Column(db.Integer, primary_key=True)
    casa_id = db.Column(db.Integer, db.ForeignKey("casas.id"), nullable=False)
    nombre = db.Column(db.String(120), nullable=False)
    cedula = db.Column(db.String(20), unique=True, nullable=False)
    telefono = db.Column(db.String(20))
    email = db.Column(db.String(120))
    tipo = db.Column(db.String(20), nullable=False)
    fecha_ingreso = db.Column(db.Date, default=date.today)
    activo = db.Column(db.Boolean, default=True)
    foto = db.Column(db.String(255))

    vehiculos = db.relationship("Vehiculo", backref="residente", lazy=True)

    def __repr__(self):
        return f"<Residente {self.nombre} ({self.cedula})>"
