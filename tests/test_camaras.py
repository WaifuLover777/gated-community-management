from core import camaras


def test_backend_override_pisa_config(app):
    with app.app_context():
        capturadas = []
        camaras._capturar_cv2 = lambda fuente: capturadas.append(fuente) or b"x"
        data, origen = camaras.capturar("cabina", "webcam", "2")
        assert data == b"x" and origen == "webcam:2" and capturadas[-1] == 2
        _, origen = camaras.capturar("cabina", "webcam", "abc")
        assert origen == "webcam:0" and capturadas[-1] == 0
        _, origen = camaras.capturar("frontal", "ip_movil", "http://x/video")
        assert origen == "http://x/video" and capturadas[-1] == "http://x/video"
