"""Color dominante de un vehículo desde la imagen (OpenCV + HSV, sin modelos)."""
import numpy as np


def _tono_a_nombre(h):
    if h < 10 or h >= 160:
        return "rojo"
    if h < 22:
        return "naranja"
    if h < 33:
        return "amarillo"
    if h < 86:
        return "verde"
    if h < 100:
        return "cian"
    if h < 130:
        return "azul"
    if h < 150:
        return "morado"
    return "rosa"


def color_dominante(imagen_bytes):
    """Nombre del color dominante del vehículo, o None si no hay imagen."""
    if not imagen_bytes:
        return None
    import cv2
    arr = np.frombuffer(imagen_bytes, dtype=np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None:
        return None
    alto, ancho = img.shape[:2]
    roi = img[int(alto * 0.35):int(alto * 0.80), int(ancho * 0.20):int(ancho * 0.80)]
    if roi.size == 0:
        roi = img
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV).reshape(-1, 3)
    H, S, V = hsv[:, 0], hsv[:, 1], hsv[:, 2]
    cromatico = S >= 60
    if cromatico.mean() < 0.25:
        v = float(np.median(V))
        return "negro" if v < 60 else "gris" if v < 170 else "blanco"
    return _tono_a_nombre(int(np.bincount(H[cromatico], minlength=180).argmax()))
