# Datawarehouse - Moreno Baldivieso

Sistema de extracción de datos para el datawarehouse de Moreno Baldivieso. Este proyecto permite extraer datos desde dos fuentes principales: una base de datos Aurora MySQL y una API GraphQL, guardando los resultados en archivos CSV.

## 📋 Descripción

Este proyecto proporciona herramientas para extraer datos de diferentes fuentes y prepararlos para su uso en un datawarehouse. Incluye tres métodos principales de extracción:

1. **Extracción desde Base de Datos**: Ejecuta consultas SQL directamente en una base de datos Aurora MySQL
2. **Extracción desde API**: Realiza peticiones GraphQL a una API REST y procesa las respuestas
3. **Extracción mediante CURL**: Ejecuta comandos curl almacenados en archivos de texto con soporte para paginación automática

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

## 📁 Estructura del Proyecto

```
Datawarehouse/
├── api_requests.py          # Script para extraer datos desde la API GraphQL
├── bd.py                    # Script para extraer datos desde la base de datos
├── run_curl.py              # Script interactivo para ejecutar comandos curl
├── requirements.txt         # Dependencias de Python
├── curls/                   # Archivos con comandos curl
│   ├── Dim_Asuntos.txt
│   ├── Dim_Usuarios.txt
│   ├── Hechos_Tiempos.txt
│   └── login.txt
├── queries/                 # Consultas SQL
│   ├── Dim_Asuntos.sql
│   ├── Dim_Usuario.sql
│   ├── Hechos_Capacidad.sql
│   └── Hechos_Tiempos.sql
├── results_api/             # Resultados de extracciones desde API
│   ├── Dim_Asuntos.csv
│   └── Dim_Usuario.csv
├── results_bd/              # Resultados de extracciones desde BD
│   ├── Dim_Asuntos.csv
│   ├── Dim_Usuario.csv
│   ├── Hechos_Capacidad.csv
│   └── Hechos_Tiempos.csv
└── extras/                  # Archivos adicionales
    ├── emba.postman_collection.json
    └── mb.ovpn
```

## 🔧 Uso

### 1. Extracción desde Base de Datos (`bd.py`)

Ejecuta todas las consultas SQL en la carpeta `queries/` y guarda los resultados en CSV.

```bash
python bd.py
```

**Características:**
- Conecta directamente a la base de datos Aurora MySQL (sin VPN)
- Ejecuta todos los archivos `.sql` en la carpeta `queries/`
- Guarda los resultados en `results_bd/` (o `results/` según configuración)
- Soporta múltiples consultas en batch

**Configuración:**
Las credenciales de la base de datos están configuradas en `bd.py`. Puedes usar variables de entorno:
- `DB_HOST` - Host de la base de datos
- `DB_PORT` - Puerto (default: 3306)
- `DB_NAME` - Nombre de la base de datos
- `DB_USER` - Usuario
- `DB_PASSWORD` - Contraseña

### 2. Extracción desde API (`api_requests.py`)

Realiza peticiones GraphQL a la API y guarda los resultados en CSV.

```bash
python api_requests.py
```

**Características:**
- Autenticación automática mediante login
- Soporte para paginación automática
- Extrae datos de:
  - `Dim_Asuntos` (BusinessMeta)
  - `Dim_Usuario` (Users)
  - `Hechos_Tiempos` (TimesByFiltersPaged)
- Guarda resultados en `results_api/`
- Convierte respuestas JSON anidadas a CSV plano

**Nota:** Las credenciales de login están hardcodeadas en el script. Considera usar variables de entorno para mayor seguridad.

### 3. Extracción mediante CURL (`run_curl.py`)

Script interactivo que permite ejecutar comandos curl almacenados en archivos.

```bash
python run_curl.py
```

**Características:**
- Menú interactivo para seleccionar qué curl ejecutar
- Soporte para paginación automática en queries GraphQL
- Guarda resultados en formato JSON y CSV en `results_curl/`
- Permite ejecutar múltiples curls en la misma sesión

## 📊 Datos Extraídos

### Dimensiones
- **Dim_Asuntos**: Información de asuntos/negocios (BusinessMeta)
- **Dim_Usuario**: Información de usuarios del sistema

### Hechos
- **Hechos_Tiempos**: Registros de tiempos trabajados
- **Hechos_Capacidad**: Datos de capacidad (solo desde BD)

## 🔐 Seguridad

⚠️ **Importante**: Este proyecto contiene credenciales hardcodeadas. Para uso en producción:

1. Usa variables de entorno para credenciales
2. No subas archivos con credenciales a repositorios públicos
3. Considera usar un gestor de secretos (AWS Secrets Manager, etc.)

## 🛠️ Funcionalidades Adicionales

### Listar tablas de la base de datos

Puedes modificar `bd.py` para usar la función `list_database_tables()` que lista todas las tablas disponibles en la base de datos.

## 📝 Notas

- Los scripts manejan automáticamente la paginación en las respuestas de la API
- Los datos anidados de JSON se aplanan automáticamente al convertir a CSV
- Los archivos CSV se guardan con codificación UTF-8
- Los scripts crean automáticamente las carpetas de resultados si no existen

## 🤝 Contribuciones

Para agregar nuevas extracciones:

1. **Para consultas SQL**: Agrega un archivo `.sql` en `queries/`
2. **Para queries GraphQL**: Modifica `api_requests.py` o agrega un archivo `.txt` en `curls/`

## 📄 Licencia

Este proyecto es de uso interno de Moreno Baldivieso.

