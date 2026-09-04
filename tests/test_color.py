import cv2
import numpy as np

from core.reconocimiento.color import color_dominante


def _img(bgr):
    a = np.full((120, 120, 3), bgr, dtype=np.uint8)
    return cv2.imencode(".png", a)[1].tobytes()


def test_colores_basicos():
    assert color_dominante(_img((0, 0, 255))) == "rojo"
    assert color_dominante(_img((255, 0, 0))) == "azul"
    assert color_dominante(_img((0, 255, 0))) == "verde"
    assert color_dominante(_img((255, 255, 255))) == "blanco"
    assert color_dominante(_img((0, 0, 0))) == "negro"
    assert color_dominante(_img((128, 128, 128))) == "gris"


def test_sin_imagen():
    assert color_dominante(None) is None
    assert color_dominante(b"no-jpg") is None
