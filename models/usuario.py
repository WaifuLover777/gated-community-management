from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db

class Usuario(db.Model):
    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    rol = db.Column(db.String(20), default="admin")
    residente_id = db.Column(db.Integer, db.ForeignKey("residentes.id"))
    foto = db.Column(db.String(255))
    creado_en = db.Column(db.DateTime, default=datetime.utcnow)

    residente = db.relationship(
        "Residente", backref="usuario", foreign_keys=[residente_id]
    )

    def set_password(self, raw):
        self.password_hash = generate_password_hash(raw)

    def check_password(self, raw):
        return check_password_hash(self.password_hash, raw)

    def __repr__(self):
        return f"<Usuario {self.email} ({self.rol})>"
