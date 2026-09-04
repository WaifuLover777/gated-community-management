from extensions import db

class Casa(db.Model):
    __tablename__ = "casas"

    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.String(20), unique=True, nullable=False)
    manzana = db.Column(db.String(20))
    villa = db.Column(db.String(20))
    tipo = db.Column(db.String(30))
    color = db.Column(db.String(30))
    area_m2 = db.Column(db.Float, default=0)
    alicuota = db.Column(db.Float, default=0)
    capacidad = db.Column(db.Integer)
    personas = db.Column(db.Integer)
    estado = db.Column(db.String(20), default="ocupada")
    pin_registro = db.Column(db.String(6), nullable=True, index=True)

    residentes = db.relationship("Residente", backref="casa", lazy=True)
    cuotas = db.relationship("Cuota", backref="casa", lazy=True)
    visitas = db.relationship("Visita", backref="casa", lazy=True)

    def __repr__(self):
        return f"<Casa {self.numero}>"
