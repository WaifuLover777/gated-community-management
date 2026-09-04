from extensions import db

class AreaComun(db.Model):
    __tablename__ = "areas_comunes"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(80), nullable=False)
    descripcion = db.Column(db.String(255))
    hora_apertura = db.Column(db.String(5), default="08:00")
    hora_cierre = db.Column(db.String(5), default="22:00")
    activo = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f"<AreaComun {self.nombre}>"
