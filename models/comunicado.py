from datetime import datetime
from extensions import db

class Comunicado(db.Model):
    __tablename__ = "comunicados"

    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(150), nullable=False)
    contenido = db.Column(db.Text, nullable=False)
    tipo = db.Column(db.String(20), default="anuncio")
    publicado_en = db.Column(db.DateTime, default=datetime.utcnow)

    fecha_publicacion = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    publicado_por = db.Column(db.String(120))
    activo = db.Column(db.Boolean, default=True)

    @property
    def programado(self):
        return bool(self.fecha_publicacion and self.fecha_publicacion > datetime.utcnow())

    def __repr__(self):
        return f"<Comunicado {self.titulo}>"
