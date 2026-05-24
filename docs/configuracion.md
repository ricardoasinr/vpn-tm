# Configuración — Credenciales y Variables de Entorno

## Archivos de Configuración

El proyecto tiene tres archivos de configuración en `config/`:

| Archivo | Qué configura |
|---------|--------------|
| `config/api.py` | URL, credenciales y tenant de la API |
| `config/database.py` | Conexión a Aurora MySQL |
| `config/telegram.py` | Bot token y chat ID de Telegram |

Todos leen primero la variable de entorno correspondiente y, si no existe, usan el valor por defecto hardcodeado.

---

## Configuración de la API (`config/api.py`)

```python
API_CONFIG = {
    'base_url':          os.getenv('API_BASE_URL',          'https://apinewtm.com'),
    'graphql_endpoint':  os.getenv('API_GRAPHQL_ENDPOINT',  '/graphql/'),
    'auth_endpoint':     os.getenv('API_AUTH_ENDPOINT',     '/api/auth/token'),
    'tenant_name':       os.getenv('API_TENANT_NAME',       'emba'),
    'username':          os.getenv('API_USERNAME',          'hmarquez@emba.com.bo'),
    'password':          os.getenv('API_PASSWORD',          '...'),
    'origin':            os.getenv('API_ORIGIN',            'https://azure-function.timemanagerweb.com')
}
```

### Variables de entorno disponibles

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `API_BASE_URL` | URL base del servidor | `https://apinewtm.com` |
| `API_GRAPHQL_ENDPOINT` | Ruta del endpoint GraphQL | `/graphql/` |
| `API_AUTH_ENDPOINT` | Ruta del endpoint de autenticación | `/api/auth/token` |
| `API_TENANT_NAME` | Nombre del tenant (va en el header `tenant-name`) | `emba` |
| `API_USERNAME` | Email/usuario para login | `usuario@empresa.com` |
| `API_PASSWORD` | Contraseña para login | `contraseña` |
| `API_ORIGIN` | Header `Origin` requerido por la API | `https://azure-function.timemanagerweb.com` |

---

## Configuración de la Base de Datos (`config/database.py`)

```python
DB_CONFIG = {
    'host':     os.getenv('DB_HOST',     'tmdb-aurora-cluster.cluster-ro-cmt9q0z4t4rd.us-east-1.rds.amazonaws.com'),
    'port':     int(os.getenv('DB_PORT', '3306')),
    'database': os.getenv('DB_NAME',     'tm_emba'),
    'user':     os.getenv('DB_USER',     'tm_emba_readonly'),
    'password': os.getenv('DB_PASSWORD', '...')
}
```

### Variables de entorno disponibles

| Variable | Descripción | Valor por defecto |
|----------|-------------|-------------------|
| `DB_HOST` | Host del servidor Aurora | `tmdb-aurora-cluster...rds.amazonaws.com` |
| `DB_PORT` | Puerto MySQL | `3306` |
| `DB_NAME` | Nombre de la base de datos | `tm_emba` |
| `DB_USER` | Usuario de la base de datos | `tm_emba_readonly` |
| `DB_PASSWORD` | Contraseña del usuario | — |

**Nota:** El usuario `tm_emba_readonly` tiene permisos de solo lectura. La conexión requiere VPN activa apuntando al cluster Aurora en `us-east-1`.

---

## Configuración de Telegram (`config/telegram.py`)

```python
TELEGRAM_CONFIG = {
    'bot_token': os.getenv('TELEGRAM_BOT_TOKEN', '...'),
    'chat_id':   os.getenv('TELEGRAM_CHAT_ID',   '...')
}
```

### Variables de entorno disponibles

| Variable | Descripción |
|----------|-------------|
| `TELEGRAM_BOT_TOKEN` | Token del bot obtenido desde @BotFather |
| `TELEGRAM_CHAT_ID` | ID del chat o grupo destino del reporte |

**Cómo obtener el chat_id:** Enviar un mensaje al bot y consultar `https://api.telegram.org/bot<TOKEN>/getUpdates`.

---

## Configuración con Archivo `.env`

El archivo `config/telegram.py` carga automáticamente el archivo `.env` si `python-dotenv` está instalado. Para los otros módulos de configuración, crear un `.env` en la raíz del proyecto y cargarlo manualmente o configurar las variables de entorno en el sistema.

### Crear el archivo `.env`

```bash
# Crear desde cero (no incluido en el repositorio)
cp .env.example .env   # si existe el ejemplo
# o crear manualmente:
```

```env
# .env — NO subir a control de versiones

# API
API_BASE_URL=https://apinewtm.com
API_TENANT_NAME=emba
API_USERNAME=tu_usuario@empresa.com
API_PASSWORD=tu_contraseña

# Base de Datos
DB_HOST=tmdb-aurora-cluster.cluster-ro-cmt9q0z4t4rd.us-east-1.rds.amazonaws.com
DB_PORT=3306
DB_NAME=tm_emba
DB_USER=tm_emba_readonly
DB_PASSWORD=tu_contraseña_db

# Telegram
TELEGRAM_BOT_TOKEN=1234567890:ABCDEF...
TELEGRAM_CHAT_ID=123456789
```

### Cargar `.env` en scripts Python

```python
from dotenv import load_dotenv
load_dotenv()
# A partir de aquí, os.getenv() lee del .env
```

---

## Configuración de la VPN

El acceso a la base de datos Aurora requiere VPN. El archivo de configuración OpenVPN está en:

```
resources/vpn/mb.ovpn
```

### Conectar en Linux/Mac

```bash
sudo openvpn --config resources/vpn/mb.ovpn
```

### Conectar en Windows

1. Instalar [OpenVPN Connect](https://openvpn.net/vpn-client/) o OpenVPN GUI.
2. Importar el archivo `mb.ovpn`.
3. Conectar antes de ejecutar cualquier script que use la base de datos.

### Verificar conectividad

```bash
# Verificar que el puerto 3306 es accesible
nc -zv tmdb-aurora-cluster.cluster-ro-cmt9q0z4t4rd.us-east-1.rds.amazonaws.com 3306
```

---

## Configuración de la Colección Postman

Para explorar la API manualmente, importar la colección en Postman:

```
resources/postman/emba.postman_collection.json
```

La colección incluye los endpoints de autenticación y los queries GraphQL documentados.

---

## Seguridad

> **Advertencia:** El proyecto incluye credenciales hardcodeadas en los archivos de configuración. Para uso en producción o en repositorios compartidos:

1. Usar variables de entorno o un archivo `.env` (no commitear al repo).
2. Agregar `.env` al `.gitignore`.
3. Considerar AWS Secrets Manager, HashiCorp Vault u otro gestor de secretos para entornos productivos.
4. Rotar credenciales si se detecta exposición accidental en el repositorio.
