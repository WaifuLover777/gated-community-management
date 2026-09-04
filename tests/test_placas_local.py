"""Verifica el pegamento del backend ANPR `local` sin depender de la precisión"""

import types

import numpy as np
from pytest import MonkeyPatch

from core.reconocimiento import placas


class _BBox:
    def __init__(self, x1, y1, x2, y2):
        self.x1, self.y1, self.x2, self.y2 = x1, y1, x2, y2

class _Det:
    def __init__(self, bbox, conf):
        self.bounding_box, self.confidence = bbox, conf

class _Pred:
    def __init__(self, plate):
        self.plate = plate


def test_leer_local_normaliza_y_recorta(monkeypatch: MonkeyPatch):
    img_jpg = _jpg(np.full((300, 500, 3), 200, np.uint8))
    recortes = []

    fake_det = types.SimpleNamespace(
        predict=lambda img: [_Det(_BBox(-5, 120, 360, 190), 0.4),
                             _Det(_BBox(10, 10, 40, 30), 0.9)])
    def _ocr_run(recorte):
        recortes.append(recorte.shape)
        return [_Pred("pce1234")]
    fake_ocr = types.SimpleNamespace(run=_ocr_run)
    monkeypatch.setattr(placas, "_modelos_local", lambda: (fake_det, fake_ocr))

    out = placas._leer_local(img_jpg, pista="ignorada.jpg")
    assert out == {"placa": "PCE-1234", "confianza": 0.9}
    assert recortes and recortes[0][0] > 0 and recortes[0][1] > 0


def test_leer_local_sin_imagen():
    assert placas._leer_local(b"", pista=None) is None


def _jpg(arr):
    import cv2
    return cv2.imencode(".jpg", arr)[1].tobytes()
