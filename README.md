# Sistema de Gestión de Residentes — Villa Los Ceibos

Sistema web para la urbanización **Villa Los Ceibos** (Guayas, Ecuador). Centraliza
residentes, viviendas, vehículos, alícuotas, multas, visitas, reservas, paquetería,
incidencias y control de accesos, con **garita inteligente** (QR, lectura de placas
y reconocimiento facial) y funcionalidades separadas por rol.

Roles: **admin**, **guardia**, **residente**.

---

## Stack

| Capa | Tecnología |
|---|---|
| Lenguaje | Python 3.10+ (probado en 3.13) |
| Framework | Flask 3.1 (application factory + blueprints) |
| ORM | SQLAlchemy 2 + Flask-Migrate (Alembic) |
| Base de datos | SQLite (por defecto) / PostgreSQL (`DATABASE_URL`) |
| Seguridad | CSRF (Flask-WTF), rate limiting (Flask-Limiter), hash scrypt (Werkzeug) |
| Configuración | python-decouple (`.env`) |
| PDF | ReportLab |
| QR | qrcode (generación) + OpenCV `QRCodeDetector` (lectura), firmado con itsdangerous |
| Placas (ANPR) | `sim` / `local` (open-image-models + fast-plate-ocr, ONNX en CPU) / `platerecognizer` (API) |
| Rostros | `sim` / `local` (InsightFace + onnxruntime, embeddings y similitud coseno) |
| Tests | pytest (113 tests) |

---

## Arquitectura

```
gated-community-management/
├── app.py              # Application factory, blueprints y comandos CLI
├── config.py           # Configuración desde .env + creación de carpetas de datos
├── extensions.py       # db, migrate, csrf, limiter
├── models/             # 18 modelos ORM, uno por entidad
├── core/
│   ├── decorators.py   # login_required, admin_required, guardia_required, residente_required
│   ├── utils.py        # PIN, tokens, subida de imágenes, fechas UTC/local
│   ├── validators.py   # validación de placas y datos de entrada
│   ├── notificaciones.py  # backend pluggable: consola | email (SMTP)
│   ├── camaras.py      # captura: ip_movil | webcam | emulador_archivo | subida
│   └── reconocimiento/ # placas.py, rostros.py, qr.py, color.py
├── modules/            # Un módulo por dominio: routes.py + services.py
│   ├── auth/  dashboard/  residentes/  pagos/  visitas/  comunicados/
│   ├── usuarios/  accesos/  portal/  guardia/  garita/
│   └── incidencias/  reservas/  multas/  paqueteria/  autorizados/
├── api/                # API JSON protegida por token (X-API-Key)
├── migrations/         # 17 migraciones Alembic
├── templates/          # Jinja: raíz (admin), guardia/, portal/
├── static/             # CSS, iconos y manifest (PWA del portal)
├── seeds.py            # Datos de prueba (flask seed)
└── tests/              # 25 archivos de test
```

**Principios:** rutas finas / lógica en `services.py`, control de acceso por rol en
decoradores, configuración por entorno, esquema versionado con migraciones y
backends intercambiables (cámara, ANPR, rostro, notificaciones) para poder correr
todo en una laptop sin hardware real.

---

## Instalación

### Windows (cmd)

```cmd
cd /d C:\ruta\a\gated-community-management

:: 1. Entorno virtual
python -m venv venv
venv\Scripts\activate

:: 2. Dependencias
pip install -r requirements.txt

:: 3. Variables de entorno
copy .env.example .env
:: Genera una clave y pégala en SECRET_KEY= dentro del .env
python -c "import secrets; print(secrets.token_hex(32))"

:: 4. Base de datos + datos de prueba
set FLASK_APP=app.py
python -m flask db upgrade
python -m flask seed

:: 5. Ejecutar
python app.py
```

### Linux / macOS

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python -c "import secrets; print(secrets.token_hex(32))"
export FLASK_APP=app.py
flask db upgrade
flask seed
python app.py
```

Abrir <http://127.0.0.1:5000>

> **`SECRET_KEY` es obligatoria.** Sin ella la app solo arranca si `FLASK_DEBUG=True`
> (genera una efímera y las sesiones se invalidan en cada reinicio).

**Notas de cmd:** cada variable va en su propia línea con `set NOMBRE=valor` (sin
comillas ni espacios alrededor del `=`); la sintaxis `VAR=valor comando` es de bash y
cmd no la reconoce. Las variables duran solo esa ventana de cmd, así que lo cómodo es
dejar `SECRET_KEY` en el `.env`. Se usa `python -m flask` por si el ejecutable `flask`
no está en el `PATH`.

---

## Credenciales de prueba (`flask seed`)

| Rol | Correo | Contraseña |
|---|---|---|
| Administrador | `admin@urb.com` | `admin123` |
| Guardia | `guardia@urb.com` | `guardia123` |
| Residente | `residente@urb.com` | `residente123` |

Los residentes reales se registran solos en `/registro` con el **PIN de la villa**
que genera el admin desde `/residentes/casas` (un solo propietario activo por casa).

---

## Módulos por rol

### Administrador
| Ruta | Función |
|---|---|
| `/dashboard` | Indicadores generales |
| `/residentes/casas` | Villas: alta, edición, capacidad y generación de PIN de registro |
| `/residentes/` · `/residentes/vehiculos` | Residentes y vehículos |
| `/pagos/` | Alícuotas: listado, confirmación y rechazo de comprobantes |
| `/pagos/generar` · `/pagos/extraordinaria` | Cuota ordinaria mensual y cuota extraordinaria |
| `/pagos/reporte` | Cobranza: % recaudado, esperado vs. real y morosos |
| `/pagos/comprobante/<id>` | Comprobante PDF (ReportLab) |
| `/multas` | Emisión y cambio de estado de multas |
| `/incidencias` | PQR de residentes y seguimiento de estado |
| `/areas` | Áreas comunes reservables |
| `/comunicados/` | Comunicados (crear, editar, archivar) |
| `/visitas/` | Visitas registradas |
| `/accesos` | Bitácora de accesos |
| `/lista-negra` | Placas vetadas |
| `/usuarios` | Usuarios del sistema |

### Guardia
| Ruta | Función |
|---|---|
| `/guardia` | Panel de turno |
| `/guardia/control` | **Garita inteligente**: captura de cámaras, QR, placas y rostro |
| `/guardia/visitas` | Visitas pendientes: autorizar entrada y marcar salida |
| `/guardia/vehiculos` · `/guardia/residentes` | Consulta rápida |
| `/guardia/novedades` | Bitácora de novedades del turno |
| `/guardia/paqueteria` | Recepción y entrega de paquetes |
| `/guardia/comunicados` | Comunicados vigentes |

### Residente (portal, PWA con `sw.js` y manifest)
| Ruta | Función |
|---|---|
| `/portal` | Inicio: deuda, cuotas y comunicados |
| `/portal/cuotas` · `/portal/cuotas/<id>/pagar` | Estado de cuenta y subida de comprobante |
| `/portal/multas/<id>/pagar` | Pago de multas |
| `/portal/vehiculos` | Alta, edición y baja de vehículos |
| `/portal/visitas/nueva` · `/portal/visitas/<id>/qr` | Invitación con PIN + QR |
| `/portal/qr` | QR personal firmado del residente |
| `/portal/autorizados` | Personas recurrentes con vigencia y QR propio |
| `/portal/reservas` | Reserva de áreas comunes |
| `/portal/incidencias` | Reportes PQR |
| `/portal/paqueteria` | Paquetes recibidos |
| `/portal/notificaciones` | Bandeja (contador en la barra) |
| `/portal/rostro` | Enrolamiento facial **con consentimiento explícito** |
| `/portal/mi-casa/personas` | Personas que habitan la villa |

---

## Garita inteligente

Tres cámaras lógicas (`frontal`, `trasera`, `cabina`), cada una con backend propio:

| Backend | Descripción |
|---|---|
| `emulador_archivo` | Usa la imagen más reciente de `data/camaras/<nombre>/` (por defecto) |
| `ip_movil` | Stream MJPEG de un celular (IP Webcam / DroidCam) |
| `webcam` | Webcam local por índice (0 = integrada) |
| `subida` | El guardia sube el frame desde la UI |

El guardia puede cambiar backend y fuente en caliente desde `/guardia/control`.

**Reglas aplicadas al resolver un acceso:**
- Lista negra de placas → acceso denegado con alerta.
- Anti-passback: se rechaza una entrada si la placa ya figura dentro.
- Discrepancia entre placa frontal y trasera → se registra como observación.
- Vehículo de residente moroso → entrada denegada; la salida siempre se permite.
- Placa desconocida → verificación manual, con el color dominante del vehículo como pista.
- Rostros: identifica múltiples ocupantes y solo compara contra residentes **activos**.
- La foto de evidencia se guarda en `static/evidencia/` y caduca según `EVIDENCIA_RETENCION_DIAS`.

---

## API JSON

Todos los endpoints van bajo `/api` y exigen la cabecera `X-API-Key` con el valor de
`API_TOKEN`. Si `API_TOKEN` está vacío la API responde **503** (deshabilitada); con
token incorrecto, **401**. El blueprint está exento de CSRF.

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/api/vehiculos/buscar-placa/<placa>` | Residente, vehículo y estado financiero |
| POST | `/api/accesos/registrar` | Registra un acceso en la bitácora |
| POST | `/api/visitas/validar-pin` | Valida el PIN de un visitante (10/min) |
| POST | `/api/qr/validar` | Valida un QR por texto (`contenido`) o imagen (30/min) |
| POST | `/api/placas/leer` | Lee placa frontal/trasera y resuelve el acceso (60/min) |
| POST | `/api/rostros/identificar` | Identifica ocupantes en una imagen (60/min) |

---

## Configuración (`.env`)

| Variable | Por defecto | Descripción |
|---|---|---|
| `SECRET_KEY` | — | **Obligatoria** fuera de debug |
| `DATABASE_URL` | `sqlite:///data/urbanizacion.db` | Cadena de conexión |
| `FLASK_DEBUG` | `False` | Nunca `True` en producción |
| `SESSION_COOKIE_SECURE` | `False` | `True` cuando se sirve con HTTPS |
| `API_TOKEN` | vacío | Vacío = API deshabilitada (503) |
| `RECARGO_MORA_MENSUAL` | `0.10` | Recargo acumulativo por mes de atraso |
| `NOTIF_BACKEND` | `consola` | `consola` o `email` (requiere `SMTP_*`) |
| `SMTP_HOST` / `PORT` / `TLS` / `USER` / `PASSWORD` / `FROM` | — | Envío de correo |
| `CAMARA_{FRONTAL,TRASERA,CABINA}_BACKEND` | `emulador_archivo` | Fuente de cada cámara |
| `CAMARA_{...}_URL` | vacío | Stream o índice de webcam |
| `RECOG_PLACA_BACKEND` | `sim` | `sim` / `local` / `platerecognizer` |
| `PLATERECOGNIZER_TOKEN` | vacío | Solo para el backend `platerecognizer` |
| `RECOG_ROSTRO_BACKEND` | `sim` | `sim` / `local` (InsightFace) |
| `RECOG_ROSTRO_UMBRAL` | `0.45` | Similitud coseno mínima para identificar |
| `EVIDENCIA_RETENCION_DIAS` | `30` | Antigüedad máxima de las fotos de evidencia |
| `TZ_OFFSET_HORAS` | `-5` | Zona horaria local (Ecuador). Se lee de `os.environ`, **no** del `.env` |

Sesión: cookie `HttpOnly`, `SameSite=Lax`, vida de 8 horas. Subidas: máx. 25 MB, solo JPG/PNG.

---

## Tests

```cmd
set SECRET_KEY=test
python -m pytest -q
```

(en Linux/macOS: `SECRET_KEY=test pytest -q`)

`SECRET_KEY` es necesaria porque la factory se ejecuta al importar `app.py`; si ya la
tienes en el `.env`, basta con `python -m pytest -q`. Son 113 tests, usan SQLite y
backends `sim`, así que no necesitan cámaras, internet ni modelos descargados.

---

## Comandos CLI

```cmd
set FLASK_APP=app.py
python -m flask db upgrade          :: aplica las migraciones pendientes
python -m flask db migrate -m "msg" :: genera una migración tras cambiar modelos
python -m flask seed                :: carga los datos de prueba
python -m flask purgar-evidencia    :: borra fotos de accesos según EVIDENCIA_RETENCION_DIAS
```

Todos requieren `SECRET_KEY` (del `.env` o con `set SECRET_KEY=...`) y una base ya
creada: sin `flask db upgrade` previo fallan con `no such table`.

---

## Mantenimiento

- La base SQLite vive en `data/urbanizacion.db`; las capturas emuladas en `data/camaras/`.
- Comprobantes de pago en `static/comprobantes/`, evidencia de accesos en `static/evidencia/`.
- Cambios de modelos: `flask db migrate -m "mensaje"` y `flask db upgrade` (ver Comandos CLI).
- Los datos biométricos solo se guardan con consentimiento explícito del residente, y
  la evidencia se purga según la política de retención.
