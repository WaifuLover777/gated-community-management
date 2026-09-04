"""Prueba la detección de auto sobre una FOTO (sin cámara/login)."""
import sys

from app import create_app
from core.reconocimiento import placas, color
from models import Vehiculo


def main(ruta):
    data = open(ruta, "rb").read()
    app = create_app()
    with app.app_context():
        lectura = placas.leer_placa(data, pista=ruta)
        col = color.color_dominante(data)
        print("Placa leída :", lectura)
        print("Color       :", col)
        if not lectura:
            print("=> ANPR no encontró placa en la imagen.")
            return
        v = Vehiculo.query.filter_by(placa=lectura["placa"]).first()
        if not v:
            print(f"=> Placa {lectura['placa']} NO registrada -> verificación manual.")
            return
        res = v.residente
        casa = getattr(res, "casa", None)
        print(f"=> AUTORIZA: {v.marca} {v.modelo} de {res.nombre} "
              f"(casa {getattr(casa, 'numero', '?')})")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("uso: python probar_auto.py <foto_del_coche.jpg>")
    main(sys.argv[1])
