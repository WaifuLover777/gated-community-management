"""Abstracción de fuentes de cámara para la garita.

El programa corre en una laptop sin cámaras reales, así que la captura se puede
emular. Backends disponibles (configurables por cámara lógica en config.py):

- ``ip_movil``    : lee un stream MJPEG de un celular vía Wi-Fi (IP Webcam / DroidCam).
- ``webcam``      : webcam local por índice (0=integrada; 1,2… = USB o Bluetooth).
- ``emulador_archivo`` : usa la imagen más reciente de ``data/camaras/<nombre>/``.
- ``subida``      : no captura sola; el frame lo sube el guardia desde la UI.

El guardia puede elegir backend y fuente en tiempo real desde la UI; esos valores
pisan los de config para esa captura. Bluetooth/USB no son un backend aparte: el
SO los expone como webcam con su propio índice, así que se eligen como ``webcam``
con el índice correspondiente.

`capturar(nombre)` devuelve los bytes JPEG del frame, o None si no hay imagen.
"""
import glob
import os
import time

from flask import current_app

_CAMARAS = ("frontal", "trasera", "cabina")

def _cfg(nombre, sufijo):
    return current_app.config.get(f"CAMARA_{nombre.upper()}_{sufijo}")

def backend_de(nombre):
    return (_cfg(nombre, "BACKEND") or "emulador_archivo").lower()

def _capturar_cv2(fuente):
    """Lee un frame con OpenCV desde una webcam (índice) o URL de stream."""
    import cv2
    cap = cv2.VideoCapture(fuente)
    try:
        ok, frame = cap.read()
        if not ok or frame is None:
            return None
        ok, buf = cv2.imencode(".jpg", frame)
        return buf.tobytes() if ok else None
    finally:
        cap.release()

def _capturar_emulador(nombre):
    carpeta = os.path.join(current_app.config["CAMARAS_DIR"], nombre)
    imgs = [f for f in glob.glob(os.path.join(carpeta, "*"))
            if f.lower().endswith((".jpg", ".jpeg", ".png"))]
    if not imgs:
        return None, None
    ultimo = max(imgs, key=os.path.getmtime)
    with open(ultimo, "rb") as fh:
        return fh.read(), os.path.basename(ultimo)

def capturar(nombre, backend=None, fuente=None):
    """Devuelve (bytes_jpeg, origen) del frame actual de la cámara lógica `nombre`.

    `backend`/`fuente` (opcionales) pisan la config para esta captura: los manda
    la UI cuando el guardia elige tipo de cámara y origen (índice o URL)."""
    if nombre not in _CAMARAS:
        return None, None
    backend = (backend or backend_de(nombre)).lower()
    if backend == "emulador_archivo":
        return _capturar_emulador(nombre)
    if backend == "webcam":
        try:
            idx = int(fuente) if fuente not in (None, "") else 0
        except ValueError:
            idx = 0
        return _capturar_cv2(idx), f"webcam:{idx}"
    if backend == "ip_movil":
        url = fuente or _cfg(nombre, "URL")
        if not url:
            return None, None
        return _capturar_cv2(url), url
    # 'subida' u otro: la imagen llega por la UI, no se captura aquí
    return None, None

def nombre_archivo_emulador(nombre):
    """Nombre del archivo de emulación actual (útil para el backend de placas 'sim')."""
    _, origen = _capturar_emulador(nombre)
    return origen
