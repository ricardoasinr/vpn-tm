# Datawarehouse - Moreno Baldivieso

Sistema de extracción de datos para el datawarehouse de Moreno Baldivieso. Este proyecto permite extraer datos desde dos fuentes principales: una base de datos Aurora MySQL y una API GraphQL, guardando los resultados en archivos CSV.

## 📋 Descripción

Este proyecto proporciona herramientas para extraer datos de diferentes fuentes y prepararlos para su uso en un datawarehouse. Incluye tres métodos principales de extracción:

1. **Extracción desde Base de Datos**: Ejecuta consultas SQL directamente en una base de datos Aurora MySQL
2. **Extracción desde API (Automática)**: Realiza peticiones GraphQL a una API REST y procesa las respuestas automáticamente
3. **Extracción desde API (Interactiva)**: Ejecuta comandos curl almacenados en archivos con soporte para paginación automática mediante menú interactivo

## 🚀 Instalación

### Requisitos

- Python 3.7 o superior
- Acceso a la base de datos Aurora MySQL (puede requerir VPN)
- Credenciales de acceso a la API

### Pasos de instalación

1. Clonar o descargar el repositorio
2. Instalar las dependencias:

```bash
pip install -r requirements.txt
```

Las dependencias incluyen:
- `pymysql>=1.0.0` - Para conexión a MySQL
- `requests>=2.31.0` - Para peticiones HTTP

3. (Opcional) Configurar variables de entorno:
   - Copia `.env.example` a `.env` y configura tus credenciales
   - O modifica directamente `config/database.py` y `config/api.py`

## 📁 Estructura del Proyecto

```
datawarehouse-mb/
├── src/
│   ├── extractors/              # Extractores principales
│   │   ├── database_extractor.py      # Extrae desde MySQL
│   │   ├── api_extractor.py           # Extracción automática de API GraphQL
│   │   └── interactive_api_extractor.py  # Extracción interactiva de API GraphQL
│   ├── api/                     # Módulos de API
│   │   ├── auth.py              # Autenticación
│   │   ├── client.py            # Cliente GraphQL
│   │   └── pagination.py        # Lógica de paginación
│   ├── database/                # Módulos de base de datos
│   │   └── connection.py        # Conexión a MySQL
│   └── utils/                   # Utilidades
│       ├── csv_writer.py         # Escritura de CSV
│       ├── json_flattener.py    # Aplanar JSON anidado
│       ├── curl_parser.py       # Parsear comandos curl
│       └── graphql_parser.py    # Parsear respuestas GraphQL
├── queries/
│   ├── sql/                     # Consultas SQL
│   │   ├── dimensions/
│   │   │   ├── dim_asuntos.sql
│   │   │   └── dim_usuarios.sql
│   │   └── facts/
│   │       ├── hechos_tiempos.sql
│   │       └── hechos_capacidad.sql
│   └── graphql/                 # Queries GraphQL
│       ├── dim_asuntos.graphql
│       ├── dim_asuntos.variables.json
│       ├── dim_usuarios.graphql
│       ├── dim_usuarios.variables.json
│       ├── hechos_tiempos.graphql
│       └── hechos_tiempos.variables.json
├── config/                      # Configuración
│   ├── database.py              # Config BD
│   └── api.py                   # Config API
├── output/                      # Resultados
│   ├── database/                # Resultados de extracciones desde BD
│   └── api/                     # Resultados de extracciones desde API
├── resources/                   # Recursos externos
│   ├── postman/
│   │   └── emba.postman_collection.json
│   └── vpn/
│       └── mb.ovpn
├── scripts/                     # Scripts de ejecución
│   ├── extract_all.py           # Ejecuta todos los extractores
│   ├── extract_dim_asuntos.py   # Extrae solo Dim_Asuntos (API)
│   ├── extract_dim_usuarios.py  # Extrae solo Dim_Usuarios (API)
│   └── extract_hechos_tiempos.py # Extrae solo Hechos_Tiempos (API)
├── requirements.txt
└── README.md
```

## 🔧 Uso

### Scripts de Ejecución Rápida

El proyecto incluye scripts convenientes en la carpeta `scripts/` para ejecutar extracciones de forma rápida:

#### Ejecutar Todos los Extractores

Ejecuta todas las extracciones (base de datos y API) en secuencia:

```bash
python scripts/extract_all.py
```

#### Ejecutar Extractores Individuales de API

Puedes ejecutar cada query GraphQL de forma individual:

**Dim_Asuntos:**
```bash
python scripts/extract_dim_asuntos.py
```

**Dim_Usuarios:**
```bash
python scripts/extract_dim_usuarios.py
```

**Hechos_Tiempos:**
```bash
python scripts/extract_hechos_tiempos.py
```

**Características de los scripts individuales:**
- Autenticación automática
- Paginación automática
- Guarda resultados en `output/api/`
- Mensajes de progreso claros
- Manejo de errores robusto

### 1. Extracción desde Base de Datos

Ejecuta todas las consultas SQL en `queries/sql/` y guarda los resultados en CSV.

```bash
python -m src.extractors.database_extractor
```

O desde la raíz del proyecto:

```bash
python src/extractors/database_extractor.py
```

**Características:**
- Conecta directamente a la base de datos Aurora MySQL
- Ejecuta todos los archivos `.sql` en `queries/sql/` (recursivo)
- Guarda los resultados en `output/database/`
- Soporta múltiples consultas en batch

**Configuración:**
Las credenciales están en `config/database.py`. Puedes usar variables de entorno:
- `DB_HOST` - Host de la base de datos
- `DB_PORT` - Puerto (default: 3306)
- `DB_NAME` - Nombre de la base de datos
- `DB_USER` - Usuario
- `DB_PASSWORD` - Contraseña

### 2. Extracción desde API (Automática)

Realiza peticiones GraphQL a la API y guarda los resultados en CSV automáticamente. Ejecuta **todos** los queries GraphQL encontrados en `queries/graphql/`.

```bash
python -m src.extractors.api_extractor
```

O desde la raíz del proyecto:

```bash
python src/extractors/api_extractor.py
```

**Características:**
- Autenticación automática mediante login
- Soporte para paginación automática
- Extrae datos de todos los queries GraphQL en `queries/graphql/`:
  - `Dim_Asuntos` (BusinessMeta)
  - `Dim_Usuarios` (Users)
  - `Hechos_Tiempos` (TimesByFiltersPaged)
- Guarda resultados en `output/api/`
- Convierte respuestas JSON anidadas a CSV plano

**Configuración:**
Las credenciales están en `config/api.py`. Puedes usar variables de entorno:
- `API_BASE_URL` - URL base de la API
- `API_USERNAME` - Usuario para login
- `API_PASSWORD` - Contraseña para login
- `API_TENANT_NAME` - Nombre del tenant

### 3. Extracción desde API (Interactiva)

Script interactivo que permite ejecutar comandos curl almacenados en archivos.

```bash
python -m src.extractors.interactive_api_extractor
```

O desde la raíz del proyecto:

```bash
python src/extractors/interactive_api_extractor.py
```

**Características:**
- Menú interactivo para seleccionar qué query ejecutar
- Lee queries GraphQL desde archivos `.graphql` y variables desde `.variables.json`
- Soporte para paginación automática en queries GraphQL
- Guarda resultados en formato JSON y CSV en `output/api/`
- Permite ejecutar múltiples queries en la misma sesión

## 📊 Datos Extraídos

### Dimensiones
- **Dim_Asuntos**: Información de asuntos/negocios (BusinessMeta)
- **Dim_Usuarios**: Información de usuarios del sistema

### Hechos
- **Hechos_Tiempos**: Registros de tiempos trabajados
- **Hechos_Capacidad**: Datos de capacidad (solo desde BD)

## 🔐 Seguridad

⚠️ **Importante**: Este proyecto contiene credenciales hardcodeadas por defecto. Para uso en producción:

1. Usa variables de entorno para credenciales (ver `config/database.py` y `config/api.py`)
2. No subas archivos con credenciales a repositorios públicos
3. Considera usar un gestor de secretos (AWS Secrets Manager, etc.)
4. Crea un archivo `.env` (no incluido en el repo) con tus credenciales

## 🛠️ Funcionalidades Adicionales

### Listar tablas de la base de datos

```python
from src.database.connection import list_database_tables
list_database_tables()
```

## 📝 Notas

- Los scripts manejan automáticamente la paginación en las respuestas de la API
- Los datos anidados de JSON se aplanan automáticamente al convertir a CSV
- Los archivos CSV se guardan con codificación UTF-8
- Los scripts crean automáticamente las carpetas de resultados si no existen
- Los nombres de archivos usan `snake_case` para consistencia
- Los scripts en `scripts/` son ejecutables directamente y proporcionan una forma conveniente de ejecutar extracciones específicas
- Usa `extract_all.py` para ejecutar todas las extracciones en una sola ejecución

## 🤝 Contribuciones

Para agregar nuevas extracciones:

1. **Para consultas SQL**: Agrega un archivo `.sql` en `queries/sql/dimensions/` o `queries/sql/facts/`
   - El extractor de base de datos los ejecutará automáticamente

2. **Para queries GraphQL automáticos**: 
   - Crea un archivo `.graphql` con el query en `queries/graphql/`
   - Crea un archivo `.variables.json` con las variables (opcional, puede estar vacío `{}`)
   - Ejemplo: `dim_nuevo.graphql` y `dim_nuevo.variables.json`
   - El extractor automático (`api_extractor.py`) los ejecutará automáticamente
   - Opcionalmente, crea un script individual en `scripts/extract_nuevo.py` siguiendo el patrón de los existentes

3. **Para queries GraphQL interactivos**: 
   - Los mismos archivos `.graphql` y `.variables.json` funcionan con el extractor interactivo
   - El extractor interactivo mostrará todos los queries disponibles en un menú

## 📄 Licencia

Este proyecto es de uso interno de Moreno Baldivieso.
