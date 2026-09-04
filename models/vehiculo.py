from extensions import db

class Vehiculo(db.Model):
    __tablename__ = "vehiculos"

    id = db.Column(db.Integer, primary_key=True)
    residente_id = db.Column(db.Integer, db.ForeignKey("residentes.id"), nullable=False)
    placa = db.Column(db.String(15), unique=True, nullable=False)
    marca = db.Column(db.String(50))
    modelo = db.Column(db.String(50))
    color = db.Column(db.String(30))

    def __repr__(self):
        return f"<Vehiculo {self.placa}>"
