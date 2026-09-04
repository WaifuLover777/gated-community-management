from extensions import db

class Cuota(db.Model):
    __tablename__ = "cuotas"
    __table_args__ = (db.UniqueConstraint("casa_id", "mes", "anio", "concepto"),)

    id = db.Column(db.Integer, primary_key=True)
    casa_id = db.Column(db.Integer, db.ForeignKey("casas.id"), nullable=False)
    mes = db.Column(db.Integer, nullable=False)
    anio = db.Column(db.Integer, nullable=False)
    monto = db.Column(db.Float, nullable=False)
    tipo = db.Column(db.String(20), default="ordinaria")
    concepto = db.Column(db.String(80), default="", nullable=False)
    recargo = db.Column(db.Float, default=0)
    estado = db.Column(db.String(20), default="pendiente")
    fecha_pago = db.Column(db.String(20))
    metodo_pago = db.Column(db.String(30))
    observacion = db.Column(db.Text)
    comprobante = db.Column(db.String(200))

    def __repr__(self):
        return f"<Cuota casa={self.casa_id} {self.mes}/{self.anio} {self.estado}>"
