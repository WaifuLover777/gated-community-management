def test_login_correcto_redirige(client):
    r = client.post("/login", data={"email": "guardia@test.com",
                                     "password": "guardia123"})
    assert r.status_code == 302
    assert "/guardia" in r.headers["Location"]


def test_login_incorrecto_no_autentica(client):
    r = client.post("/login", data={"email": "guardia@test.com",
                                     "password": "malisima"}, follow_redirects=True)
    assert "Credenciales incorrectas" in r.get_data(as_text=True)


def test_ruta_protegida_sin_sesion_redirige(client):
    r = client.get("/guardia")
    assert r.status_code == 302
    assert "/login" in r.headers["Location"]
