# Arquitectura del Sistema — Datawarehouse Moreno Baldivieso

## Visión General

El sistema es un pipeline ETL (Extracción, Transformación, Carga) diseñado para alimentar el datawarehouse de **Moreno Baldivieso**, estudio jurídico boliviano. Extrae datos desde dos fuentes heterogéneas, los transforma a formato tabular y los persiste como archivos CSV listos para consumo analítico.

```
┌─────────────────────────────────────────────────────────────────┐
│                     FUENTES DE DATOS                            │
│                                                                 │
│  ┌──────────────────────┐    ┌──────────────────────────────┐   │
│  │  Aurora MySQL (AWS)  │    │  Time Manager API (GraphQL)  │   │
│  │  tmdb-aurora-cluster │    │  https://apinewtm.com        │   │
│  │  us-east-1.rds.aws   │    │  /graphql/                   │   │
│  └─────────┬────────────┘    └──────────────┬───────────────┘   │
│            │  (VPN requerida)               │  (HTTPS + JWT)    │
└────────────┼───────────────────────────────┼───────────────────┘
             │                               │
             ▼                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                     CAPA DE EXTRACCIÓN                          │
│                                                                 │
│  ┌─────────────────────┐   ┌────────────────────────────────┐   │
│  │ DatabaseExtractor   │   │       ApiExtractor             │   │
│  │ (queries/sql/*.sql) │   │ (queries/graphql/*.graphql)    │   │
│  └─────────────────────┘   └────────────────────────────────┘   │
│                                                                 │
│             ┌──────────────────────────────────┐               │
│             │    InteractiveApiExtractor       │               │
│             │    (menú interactivo)            │               │
│             └──────────────────────────────────┘               │
└─────────────────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│                     CAPA DE TRANSFORMACIÓN                      │
│                                                                 │
│  JsonFlattener ──► aplana objetos JSON anidados                │
│  GraphQLParser ──► extrae filas de respuestas paginadas        │
│  CsvWriter     ──► escribe archivos CSV con UTF-8              │
└─────────────────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│                     SALIDA (output/)                            │
│                                                                 │
│  output/database/   ◄── resultados de consultas SQL            │
│  output/api/        ◄── resultados de queries GraphQL          │
└─────────────────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│               AUTOMATIZACIÓN Y NOTIFICACIONES                   │
│                                                                 │
│  DailyReport ──► ejecuta todos los extractores                 │
│  TelegramSender ──► envía reporte HTML al canal configurado    │
│  Daemon / Cron / Task Scheduler ──► disparo diario 23:00       │
└─────────────────────────────────────────────────────────────────┘
```

---

## Estructura de Directorios

```
vpn-tm/
├── config/                          # Configuración de conexiones
│   ├── api.py                       # URL, credenciales y tenant API
│   ├── database.py                  # Host, puerto, DB y credenciales MySQL
│   └── telegram.py                  # Token del bot y chat_id de Telegram
│
├── src/                             # Código fuente principal
│   ├── api/                         # Módulos de comunicación con la API
│   │   ├── auth.py                  # Login → obtención de JWT Bearer token
│   │   ├── client.py                # Cliente GraphQL con paginación automática
│   │   └── pagination.py            # Lógica de detección de páginas siguientes
│   ├── database/
│   │   └── connection.py            # Conexión pymysql a Aurora MySQL
│   ├── extractors/
│   │   ├── api_extractor.py         # Extractor automático (todos los .graphql)
│   │   ├── database_extractor.py    # Extractor SQL (todos los .sql)
│   │   └── interactive_api_extractor.py  # Extractor interactivo con menú
│   └── utils/
│       ├── csv_writer.py            # Escritura CSV con DictWriter
│       ├── curl_parser.py           # Parser de comandos curl a dict
│       ├── graphql_parser.py        # Extracción de filas por tipo de query
│       ├── json_flattener.py        # Aplanado recursivo de JSON anidado
│       └── telegram_sender.py       # Envío de mensajes HTML a Telegram
│
├── queries/
│   ├── sql/
│   │   ├── dimensions/
│   │   │   ├── dim_asuntos.sql      # Dimensión asuntos/expedientes
│   │   │   └── dim_usuarios.sql     # Dimensión usuarios del sistema
│   │   └── facts/
│   │       ├── hechos_tiempos.sql   # Hechos de registros de tiempo
│   │       ├── hechos_capacidad.sql # Hechos de capacidad por abogado/mes
│   │       └── hechos_estado_resultados.sql  # Hechos de estado de resultados
│   └── graphql/
│       ├── dim_asuntos.graphql      # Query BusinessMeta
│       ├── dim_asuntos.variables.json
│       ├── dim_usuarios.graphql     # Query Users
│       ├── dim_usuarios.variables.json
│       ├── hechos_tiempos.graphql   # Query TimesByFiltersPaged
│       └── hechos_tiempos.variables.json
│
├── scripts/                         # Puntos de entrada ejecutables
│   ├── extract_all.py               # Ejecuta DB + API en secuencia
│   ├── extract_dim_asuntos.py       # Solo Dim_Asuntos vía API
│   ├── extract_dim_usuarios.py      # Solo Dim_Usuarios vía API
│   ├── extract_hechos_tiempos.py    # Solo Hechos_Tiempos vía API
│   ├── daily_report.py              # Extracción completa + reporte Telegram
│   ├── run_daily_report.py          # Wrapper para ejecución manual
│   ├── run_daemon.py                # Demonio que lanza report a las 23:00
│   ├── run_report.sh                # Shell script para Linux/Mac
│   ├── run_report.bat               # Batch script para Windows
│   ├── setup_cron.sh                # Configurador de cron job (Linux/Mac)
│   └── setup_cron_windows.ps1       # Configurador de Task Scheduler (Windows)
│
├── output/
│   ├── database/                    # CSVs generados por el extractor SQL
│   └── api/                         # CSVs generados por el extractor API
│
└── resources/
    ├── postman/
    │   └── emba.postman_collection.json  # Colección Postman para pruebas
    └── vpn/
        └── mb.ovpn                  # Configuración VPN OpenVPN
```

---

## Flujo de Datos Detallado

### 1. Extracción desde Base de Datos

```
Archivo .sql
     │
     ▼
DatabaseExtractor.execute_queries_to_csv()
     │
     ├── get_db_connection() ──► pymysql.connect(Aurora MySQL via VPN)
     │
     ├── cursor.execute(query)
     │
     ├── cursor.fetchall() + cursor.description
     │
     └── csv.writer ──► output/database/<nombre>.csv
```

**Requiere:** VPN activa apuntando al cluster Aurora en `us-east-1`.

### 2. Extracción desde API (Automática)

```
Archivos queries/graphql/*.graphql
     │
     ▼
ApiExtractor.main()
     │
     ├── auth.login()
     │     └── POST /api/auth/token  ──► Bearer JWT token
     │
     ├── Para cada .graphql encontrado:
     │     │
     │     ├── load_graphql_query() ──► lee .graphql + .variables.json
     │     │
     │     └── graphql_request(token, query, variables, paginate=True)
     │           │
     │           ├── Página 1: POST /graphql/ con variables
     │           │     └── has_next_page() ──► ¿hay más páginas?
     │           ├── Página 2 ... N
     │           └── retorna lista de todas las respuestas JSON
     │
     └── graphql_to_csv(results)
           ├── extract_rows_from_graphql_response() ──► lista de dicts
           ├── flatten_dict() ──► aplana objetos anidados
           └── write_csv() ──► output/api/<nombre>.csv
```

### 3. Extracción Interactiva

Mismo flujo que el automático, pero con menú de selección por consola. Además guarda el JSON crudo en `output/api/<nombre>.json` antes de convertir a CSV.

### 4. Reporte Diario con Telegram

```
daily_report.main()
     │
     ├── execute_extractors()
     │     ├── extract_database()  ──► DatabaseExtractor
     │     └── extract_api()       ──► ApiExtractor
     │
     ├── get_file_stats(output/database/)  ──► filas + tamaño por CSV
     ├── get_file_stats(output/api/)
     │
     ├── format_telegram_message() ──► HTML con estadísticas
     │
     └── send_telegram_message()
           └── POST https://api.telegram.org/bot{token}/sendMessage
```

---

## Módulos Clave

### `src/api/auth.py`

Realiza el login a la API y retorna el Bearer token. Soporta tres nombres de campo posibles en la respuesta: `token`, `access_token` o `accessToken`.

**Endpoint:** `POST {base_url}/api/auth/token`  
**Headers:** `tenant-name`, `Origin`, `Content-Type`  
**Body:** `{ username, password }`

### `src/api/client.py`

Cliente GraphQL con paginación automática. Por cada query:
1. Construye el payload con la página actual.
2. Llama `has_next_page()` para saber si continuar.
3. Incrementa `page` y repite hasta que no haya más páginas.
4. Retorna una lista con todas las respuestas JSON (una por página).

### `src/api/pagination.py`

Detecta si hay página siguiente inspeccionando el campo `hasNextPage` (o `has_next_page`) dentro de los objetos conocidos:

| Query GraphQL         | Campo raíz              | Campo de paginación   |
|-----------------------|-------------------------|-----------------------|
| `BusinessMeta`        | `data.BusinessMeta.meta`| `hasNextPage`         |
| `Users`               | `data.Users.meta`       | `hasNextPage`         |
| `TimesByFiltersPaged` | `data.TimesByFiltersPaged` | `has_next_page`   |

### `src/utils/json_flattener.py`

Aplana recursivamente diccionarios anidados usando `_` como separador. Las listas se serializan como string JSON. Ejemplo:

```python
# Entrada
{"user": {"id": 1, "name": "Ana"}, "minutes": 60}
# Salida
{"user_id": 1, "user_name": "Ana", "minutes": 60}
```

### `src/utils/graphql_parser.py`

Mapea cada tipo de respuesta GraphQL a su array de filas:

| `data.*` key           | Array de filas               |
|------------------------|------------------------------|
| `BusinessMeta`         | `.rows[]`                    |
| `Users`                | `.users[]`                   |
| `TimesByFiltersPaged`  | `.times[]`                   |

---

## Infraestructura de Conexión

### Base de Datos

| Parámetro | Valor por defecto |
|-----------|-------------------|
| Host | `tmdb-aurora-cluster.cluster-ro-cmt9q0z4t4rd.us-east-1.rds.amazonaws.com` |
| Puerto | `3306` |
| Base de datos | `tm_emba` |
| Usuario | `tm_emba_readonly` |
| Acceso | **Solo lectura**, requiere VPN |

El cluster es de **solo lectura** (`cluster-ro`). La conexión se establece con SSL habilitado (sin verificación de CA).

### API Time Manager

| Parámetro | Valor |
|-----------|-------|
| Base URL | `https://apinewtm.com` |
| GraphQL endpoint | `/graphql/` |
| Auth endpoint | `/api/auth/token` |
| Tenant | `emba` |
| Origin | `https://azure-function.timemanagerweb.com` |

La autenticación es por **JWT Bearer token** con sesión por ejecución (no se persiste entre runs).

### Telegram Bot

El bot envía mensajes HTML a un chat configurado. La configuración se lee de variables de entorno o del archivo `config/telegram.py`.

---

## Dependencias

| Librería | Versión mínima | Uso |
|----------|----------------|-----|
| `pymysql` | 1.0.0 | Conexión a Aurora MySQL |
| `requests` | 2.31.0 | HTTP hacia la API y Telegram |
| `python-dotenv` | 1.0.0 | Carga de `.env` opcional |

**Python requerido:** 3.7+

---

## Variables de Entorno

Todas las configuraciones sensibles se pueden sobrescribir con variables de entorno. Si no se definen, se usan los valores por defecto del archivo de configuración.

| Variable | Config | Descripción |
|----------|--------|-------------|
| `DB_HOST` | `config/database.py` | Host Aurora MySQL |
| `DB_PORT` | `config/database.py` | Puerto MySQL (default: 3306) |
| `DB_NAME` | `config/database.py` | Nombre de la base de datos |
| `DB_USER` | `config/database.py` | Usuario de la base de datos |
| `DB_PASSWORD` | `config/database.py` | Contraseña |
| `API_BASE_URL` | `config/api.py` | URL base de la API |
| `API_GRAPHQL_ENDPOINT` | `config/api.py` | Ruta del endpoint GraphQL |
| `API_AUTH_ENDPOINT` | `config/api.py` | Ruta del endpoint de auth |
| `API_TENANT_NAME` | `config/api.py` | Nombre del tenant |
| `API_USERNAME` | `config/api.py` | Usuario para login |
| `API_PASSWORD` | `config/api.py` | Contraseña para login |
| `API_ORIGIN` | `config/api.py` | Header Origin para la API |
| `TELEGRAM_BOT_TOKEN` | `config/telegram.py` | Token del bot de Telegram |
| `TELEGRAM_CHAT_ID` | `config/telegram.py` | ID del chat destino |
