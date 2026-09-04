"""Reconocimiento facial con backend pluggable."""
import hashlib
import json

from flask import current_app


def _backend():
    return (current_app.config.get("RECOG_ROSTRO_BACKEND") or "sim").lower()


def serializar(emb):
    return json.dumps([round(float(x), 6) for x in emb])

def deserializar(txt):
    try:
        return json.loads(txt)
    except (TypeError, ValueError):
        return []

def comparar(emb, candidatos):
    """Devuelve (indice, score_coseno) de la mejor coincidencia en `candidatos`."""
    import numpy as np
    if emb is None or not candidatos:
        return -1, 0.0
    a = np.asarray(emb, dtype=np.float32)
    na = np.linalg.norm(a) + 1e-9
    mejor_i, mejor_s = -1, -1.0
    for i, c in enumerate(candidatos):
        b = np.asarray(c, dtype=np.float32)
        if b.shape != a.shape:
            continue
        s = float(np.dot(a, b) / (na * (np.linalg.norm(b) + 1e-9)))
        if s > mejor_s:
            mejor_i, mejor_s = i, s
    return mejor_i, mejor_s


def _detectar_caras(img_gray):
    import cv2
    ruta = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    clf = cv2.CascadeClassifier(ruta)
    caras = clf.detectMultiScale(img_gray, scaleFactor=1.1, minNeighbors=5,
                                 minSize=(60, 60))
    return list(caras)

def _embedding_sim(crop_gray):
    import cv2
    import numpy as np
    g = cv2.resize(crop_gray, (32, 32))
    h = hashlib.sha512(g.tobytes()).digest()
    vec = np.frombuffer(h, dtype=np.uint8).astype(np.float32)
    vec = vec - vec.mean()
    return (vec / (np.linalg.norm(vec) + 1e-9)).tolist()

def extraer_embeddings(imagen_bytes):
    """Lista de embeddings, uno por rostro detectado (multi-ocupante)."""
    if _backend() == "local":
        return _extraer_local(imagen_bytes)
    import cv2
    import numpy as np
    arr = np.frombuffer(imagen_bytes, dtype=np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None:
        return []
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    caras = _detectar_caras(gray)
    if not caras:
        return [_embedding_sim(gray)]
    embs = []
    for (x, y, w, h) in caras:
        embs.append(_embedding_sim(gray[y:y + h, x:x + w]))
    return embs

def _extraer_local(imagen_bytes):
    try:
        import numpy as np
        import cv2
        from insightface.app import FaceAnalysis
        global _FA
        try:
            _FA
        except NameError:
            _FA = FaceAnalysis(name="buffalo_s", providers=["CPUExecutionProvider"])
            _FA.prepare(ctx_id=-1, det_size=(640, 640))
        arr = np.frombuffer(imagen_bytes, dtype=np.uint8)
        img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        caras = _FA.get(img)
        return [f.embedding.tolist() for f in caras]
    except Exception:
        current_app.logger.exception("Backend de rostro 'local' no disponible")
        return []
