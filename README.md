# Datawarehouse — Moreno Baldivieso

Sistema ETL para el datawarehouse de **Moreno Baldivieso**. Extrae datos desde una base de datos Aurora MySQL y desde la API GraphQL de Time Manager, y los exporta como archivos CSV.

---

## Documentación

La documentación detallada está en la carpeta [`docs/`](docs/):

| Documento | Descripción |
|-----------|-------------|
| [docs/arquitectura.md](docs/arquitectura.md) | Arquitectura completa del sistema, flujo de datos, módulos clave |
| [docs/modelo-datos.md](docs/modelo-datos.md) | Modelo estrella: dimensiones, hechos, tablas fuente |
| [docs/scripts.md](docs/scripts.md) | Todos los scripts y modos de extracción con ejemplos |
| [docs/configuracion.md](docs/configuracion.md) | Credenciales, variables de entorno, VPN, Postman |
| [docs/automatizacion.md](docs/automatizacion.md) | Cron, Task Scheduler y demonio Python para reporte automático |

---

## Instalación Rápida

### Requisitos

- Python 3.7 o superior
- VPN activa (solo para extracción desde base de datos)

### 1. Clonar el repositorio

```bash
git clone <url-del-repo>
cd vpn-tm
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

Dependencias:
- `pymysql>=1.0.0` — conexión a Aurora MySQL
- `requests>=2.31.0` — HTTP para la API y Telegram
- `python-dotenv>=1.0.0` — carga de variables desde `.env`

### 3. (Opcional) Configurar credenciales con variables de entorno

```bash
# Copiar y editar el archivo de entorno
cp .env.example .env
```

Si no se configura `.env`, el sistema usa las credenciales por defecto en `config/`. Ver [docs/configuracion.md](docs/configuracion.md) para detalles completos.

### 4. Conectar a la VPN de Time Manager

> **Importante:** La VPN proporcionada por Time Manager debe estar **encendida y activa** para que cualquier extracción desde la base de datos funcione. Sin VPN, la conexión a Aurora MySQL será rechazada.

Usar el perfil OpenVPN incluido en el repositorio:

```bash
sudo openvpn --config resources/vpn/mb.ovpn
```

---

## Uso

### Extracción completa (BD + API)

```bash
python scripts/extract_all.py
```

### Solo API — todos los queries

```bash
python src/extractors/api_extractor.py
```

### Solo API — query individual

```bash
python scripts/extract_dim_asuntos.py
python scripts/extract_dim_usuarios.py
python scripts/extract_hechos_tiempos.py
```

### Solo Base de Datos

```bash
python src/extractors/database_extractor.py
```

### Modo interactivo (menú)

```bash
python src/extractors/interactive_api_extractor.py
```

### Reporte diario con notificación Telegram

```bash
# Linux/Mac
bash scripts/run_report.sh

# Windows
scripts\run_report.bat

# Directo con Python
python scripts/run_daily_report.py
```

---

## Automatización Diaria (23:00)

### Linux/Mac — Cron

```bash
bash scripts/setup_cron.sh
```

### Windows — Task Scheduler

```powershell
# Como Administrador
.\scripts\setup_cron_windows.ps1
```

### Alternativa — Demonio Python (sin configuración de sistema)

```bash
python scripts/run_daemon.py
```

Ver [docs/automatizacion.md](docs/automatizacion.md) para instrucciones detalladas.

---

## Estructura del Proyecto

```
vpn-tm/
├── config/              # Credenciales y configuración
│   ├── api.py           # API Time Manager
│   ├── database.py      # Aurora MySQL
│   └── telegram.py      # Bot de Telegram
├── src/                 # Código fuente
│   ├── api/             # Auth, cliente GraphQL, paginación
│   ├── database/        # Conexión MySQL
│   ├── extractors/      # Extractores (BD, API automático, API interactivo)
│   └── utils/           # CSV, JSON flattener, parser GraphQL, Telegram
├── queries/
│   ├── sql/             # Consultas SQL por dimensión/hecho
│   └── graphql/         # Queries GraphQL + archivos de variables
├── scripts/             # Puntos de entrada ejecutables
├── output/
│   ├── database/        # CSVs generados desde BD
│   └── api/             # CSVs generados desde API
├── resources/
│   ├── postman/         # Colección Postman para pruebas
│   └── vpn/             # Perfil OpenVPN
├── docs/                # Documentación detallada
└── requirements.txt
```

---

## Datos Extraídos

| Tabla | Fuente BD | Fuente API | Descripción |
|-------|-----------|-----------|-------------|
| `dim_asuntos` | ✓ | ✓ | Expedientes/asuntos jurídicos |
| `dim_usuarios` | ✓ | ✓ | Abogados y profesionales |
| `hechos_tiempos` | ✓ | ✓ | Registros de tiempo trabajado |
| `hechos_capacidad` | ✓ | — | Capacidad disponible por abogado/mes |
| `hechos_estado_resultados` | ✓ | — | Facturación para análisis contable |

---

## Seguridad

Los archivos de configuración incluyen credenciales por defecto. Para producción:

1. Usar variables de entorno o archivo `.env` (nunca commitear al repo).
2. Agregar `.env` al `.gitignore`.
3. Ver [docs/configuracion.md](docs/configuracion.md) para la lista completa de variables.
