"""Lectura de placas (ANPR) con backend pluggable."""
import re

from flask import current_app

_DET = _OCR = None

def _modelos_local():
    """Carga (una vez) el detector de placa y el OCR. Modelos pequeños, CPU."""
    global _DET, _OCR
    if _DET is None:
        from open_image_models import LicensePlateDetector
        from fast_plate_ocr import LicensePlateRecognizer
        det = current_app.config.get("RECOG_PLACA_DET_MODEL", "yolo-v9-t-384-license-plate-end2end")
        ocr = current_app.config.get("RECOG_PLACA_OCR_MODEL", "cct-xs-v1-global-model")
        _DET = LicensePlateDetector(detection_model=det)
        _OCR = LicensePlateRecognizer(ocr)
    return _DET, _OCR

_RE_PLACA = re.compile(r"[A-Z]{3}-?\d{3,4}", re.IGNORECASE)

def _normalizar(texto):
    m = _RE_PLACA.search(texto or "")
    if not m:
        return None
    placa = m.group(0).upper().replace(" ", "")
    if "-" not in placa:
        placa = placa[:3] + "-" + placa[3:]
    return placa

def _leer_sim(imagen_bytes, pista):
    placa = _normalizar(pista or "")
    if not placa:
        return None
    return {"placa": placa, "confianza": 0.99}

def _leer_local(imagen_bytes, pista):
    if not imagen_bytes:
        return None
    import cv2
    import numpy as np
    img = cv2.imdecode(np.frombuffer(imagen_bytes, np.uint8), cv2.IMREAD_COLOR)
    if img is None:
        return None
    try:
        det, ocr = _modelos_local()
    except Exception:
        current_app.logger.exception("Backend de placa 'local' no disponible")
        return None
    detecciones = sorted(det.predict(img), key=lambda d: d.confidence, reverse=True)
    for d in detecciones:
        b = d.bounding_box
        recorte = img[max(0, b.y1):b.y2, max(0, b.x1):b.x2]
        if recorte.size == 0:
            continue
        for pred in ocr.run(recorte):
            texto = pred if isinstance(pred, str) else getattr(pred, "plate", "")
            placa = _normalizar(texto)
            if placa:
                return {"placa": placa, "confianza": round(float(d.confidence), 2)}
    return None

def _leer_platerecognizer(imagen_bytes, pista):
    token = current_app.config.get("PLATERECOGNIZER_TOKEN")
    if not token or not imagen_bytes:
        return None
    import requests
    try:
        r = requests.post(
            "https://api.platerecognizer.com/v1/plate-reader/",
            files={"upload": ("frame.jpg", imagen_bytes)},
            headers={"Authorization": f"Token {token}"},
            timeout=15,
        )
        data = r.json()
        resultados = data.get("results") or []
        if not resultados:
            return None
        mejor = resultados[0]
        return {"placa": _normalizar(mejor.get("plate", "")) or mejor.get("plate", "").upper(),
                "confianza": float(mejor.get("score", 0))}
    except Exception:
        current_app.logger.exception("Error consultando PlateRecognizer")
        return None

def leer_placa(imagen_bytes, pista=None):
    backend = (current_app.config.get("RECOG_PLACA_BACKEND") or "sim").lower()
    if backend == "platerecognizer":
        return _leer_platerecognizer(imagen_bytes, pista)
    if backend == "local":
        return _leer_local(imagen_bytes, pista)
    return _leer_sim(imagen_bytes, pista)
