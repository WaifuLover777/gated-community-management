import re

_RE_NOMBRE = re.compile(r"^[A-Za-zÁÉÍÓÚáéíóúÑñÜü ]+$")
_RE_SOLO_DIGITOS = re.compile(r"^\d+$")
_RE_PLACA = re.compile(r"^[A-Z]{3}-?\d{3,4}$")
_RE_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

def validar_nombre(valor, *, campo="nombre", minimo=3, maximo=80, requerido=True):
    valor = (valor or "").strip()
    if not valor:
        if requerido:
            return None, f"El campo {campo} es obligatorio."
        return "", None
    if len(valor) < minimo:
        return None, f"El {campo} debe tener al menos {minimo} caracteres."
    if len(valor) > maximo:
        return None, f"El {campo} no puede superar {maximo} caracteres."
    if not _RE_NOMBRE.match(valor):
        return None, f"El {campo} solo puede contener letras y espacios."
    return valor, None

def validar_cedula(valor, *, requerido=True):
    valor = (valor or "").strip()
    if not valor:
        if requerido:
            return None, "La cédula es obligatoria."
        return "", None
    if not _RE_SOLO_DIGITOS.match(valor):
        return None, "La cédula solo puede contener números."
    if len(valor) != 10:
        return None, "La cédula debe tener 10 dígitos."
    return valor, None

def validar_telefono(valor, *, requerido=False):
    valor = (valor or "").strip()
    if not valor:
        if requerido:
            return None, "El teléfono es obligatorio."
        return "", None
    if not _RE_SOLO_DIGITOS.match(valor):
        return None, "El teléfono solo puede contener números."
    if not (7 <= len(valor) <= 10):
        return None, "El teléfono debe tener entre 7 y 10 dígitos."
    return valor, None

def validar_placa(valor, *, requerido=True):
    valor = (valor or "").strip().upper().replace(" ", "")
    if not valor:
        if requerido:
            return None, "La placa es obligatoria."
        return "", None
    if not _RE_PLACA.match(valor):
        return None, "Placa inválida. Formato: ABC-1234."
    return valor, None

def validar_email(valor, *, requerido=True, maximo=50):
    valor = (valor or "").strip().lower()
    if not valor:
        if requerido:
            return None, "El correo es obligatorio."
        return "", None
    if not _RE_EMAIL.match(valor):
        return None, "El correo no tiene un formato válido."
    if len(valor) > maximo:
        return None, f"El correo no puede superar {maximo} caracteres."
    return valor, None

def validar_password(valor, *, minimo=6, maximo=50):
    valor = valor or ""
    if len(valor) < minimo:
        return None, f"La contraseña debe tener al menos {minimo} caracteres."
    if len(valor) > maximo:
        return None, f"La contraseña no puede superar {maximo} caracteres."
    return valor, None

def limpiar_texto(valor, *, campo="texto", maximo=200, requerido=False, minimo=0):
    valor = (valor or "").strip()
    if not valor:
        if requerido:
            return None, f"El campo {campo} es obligatorio."
        return "", None
    if minimo and len(valor) < minimo:
        return None, f"El {campo} debe tener al menos {minimo} caracteres."
    if len(valor) > maximo:
        return None, f"El {campo} no puede superar {maximo} caracteres."
    return valor, None

def validar_datos_visita(nombre, cedula, placa, motivo):
    nombre, err = validar_nombre(nombre, campo="nombre del visitante")
    if err:
        return None, err
    cedula, err = validar_cedula(cedula, requerido=False)
    if err:
        return None, err
    placa, err = validar_placa(placa, requerido=False)
    if err:
        return None, err
    motivo, err = limpiar_texto(motivo, campo="motivo", maximo=70, requerido=False)
    if err:
        return None, err
    return {"nombre_visitante": nombre, "cedula_visitante": cedula,
            "placa_vehiculo": placa, "motivo": motivo}, None

def validar_entero(valor, *, campo="valor", minimo=None, maximo=None, requerido=True):
    valor = (valor or "").strip() if isinstance(valor, str) else valor
    if valor in (None, ""):
        if requerido:
            return None, f"El campo {campo} es obligatorio."
        return None, None
    try:
        n = int(valor)
    except (TypeError, ValueError):
        return None, f"El {campo} debe ser un número entero."
    if minimo is not None and n < minimo:
        return None, f"El {campo} no puede ser menor que {minimo}."
    if maximo is not None and n > maximo:
        return None, f"El {campo} no puede ser mayor que {maximo}."
    return n, None
