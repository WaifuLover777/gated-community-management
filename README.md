# Sistema de Gestión de Residentes — Villa Los Ceibos

Sistema administrativo para la urbanización **Villa Los Ceibos** (Guayas, Ecuador).
Centraliza la gestión de residentes, viviendas, vehículos, alícuotas, visitantes y
control de accesos, con funcionalidades diferenciadas por rol.

> Esta entrega corresponde a la **primera mitad** del proyecto. La fase 2 añadirá
> OCR de placas y reconocimiento facial, que consumirán la API JSON ya incluida.

---

## Stack

| Capa | Tecnología |
|---|---|
| Lenguaje | Python 3.10+ |
| Framework | Flask 3 (application factory + blueprints) |
| ORM | SQLAlchemy 2 + Flask-Migrate (Alembic) |
| Base de datos | SQLite (entrega) / PostgreSQL (escalable) |
| Configuración | python-decouple (`.env`) |
| PDF | ReportLab |
| Seguridad | Hash de contraseñas con Werkzeug (scrypt) |

---

## Arquitectura

```
urbanizacion/
├── app.py              # Application factory + registro de blueprints + CLI
├── config.py           # Configuración leída desde .env
├── extensions.py       # Instancias de db y migrate
├── .env                # Variables sensibles (no se versiona)
├── models/             # Modelos ORM, uno por entidad
├── core/               # decorators.py (roles) y utils.py (PIN, fechas, constantes)
├── modules/            # Un módulo por dominio: routes.py + services.py
│   ├── auth/  dashboard/  residentes/  pagos/
│   ├── visitas/  accesos/  guardia/  portal/  usuarios/  comunicados/
├── api/                # Endpoints JSON para la fase 2 (visión por computadora)
├── migrations/         # Migraciones generadas por Flask-Migrate
├── templates/          # Plantillas Jinja organizadas por rol
└── seeds.py            # Datos de prueba (flask seed)
```

**Principios:** separación de responsabilidades (rutas finas / lógica en `services`),
control de acceso por rol centralizado en decoradores, configuración por entorno y
esquema versionado con migraciones.

---

## Instalación (menos de 5 minutos)

```bash
# 1. Crear y activar el entorno virtual
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux / macOS

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Configurar variables de entorno
copy .env.example .env        # Windows   (cp en Linux/macOS)

# 4. Crear la base de datos y cargar datos de prueba
set FLASK_APP=app.py          # Windows   (export en Linux/macOS)
flask db upgrade
flask seed

# 5. Ejecutar
python app.py
```

Abrir en el navegador: <http://127.0.0.1:5000>

---

## Credenciales de prueba

| Rol | Correo | Contraseña |
|---|---|---|
| Administrador | `admin@urb.com` | `admin123` |
| Guardia | `guardia@urb.com` | `guardia123` |
| Residente | `residente@urb.com` | `residente123` |

---

## Gestión financiera (alícuotas)

| Función | Descripción |
|---|---|
| Alícuota mensual | El admin genera la cuota ordinaria del mes para todas las casas. |
| **Cuotas extraordinarias** | Cobro único con concepto (p. ej. "Reparación de piscina"), aplicable a **todas las casas** o a **una casa específica** (`/pagos/extraordinaria`). |
| **Recargo por mora** | Las cuotas vencidas acumulan un recargo configurable por cada mes de atraso (`RECARGO_MORA_MENSUAL`, por defecto 10% mensual). Se congela al pagar y se refleja en el comprobante PDF. |
| **Deuda consolidada** | El portal del residente muestra su deuda total (pendiente + vencido + mora). |
| **Reporte de cobranza** | Vista del admin (`/pagos/reporte`) con % de recaudación, esperado vs. recaudado y lista de morosos con su deuda total. |

---

## API (base para la fase 2)

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/api/vehiculos/buscar-placa/<placa>` | Residente + estado financiero por placa |
| POST | `/api/accesos/registrar` | Registra un acceso (validación automática) |
| POST | `/api/visitas/validar-pin` | Valida el PIN de un visitante |

---

## Notas

- La base de datos SQLite se crea en `data/urbanizacion.db`.
- Para usar PostgreSQL, define `DATABASE_URL` en el `.env`.
- `RECARGO_MORA_MENSUAL` (`.env`) define el recargo por mora; `0.10` = 10% por
  cada mes de atraso (acumulativo).
- Cualquier cambio en los modelos se aplica con
  `flask db migrate -m "mensaje"` y `flask db upgrade` (sin perder datos).
