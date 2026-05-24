# Scripts — Referencia Completa

Todos los scripts se ejecutan desde la **raíz del proyecto**. Los paths relativos (`queries/`, `output/`) dependen de que el directorio de trabajo sea la raíz.

---

## Modos de Extracción

### Modo 1 — Extracción Completa (BD + API)

Ejecuta en secuencia el extractor de base de datos y el extractor automático de API.

```bash
python scripts/extract_all.py
```

**Qué hace:**
1. Conecta a Aurora MySQL y ejecuta todos los `.sql` en `queries/sql/` (recursivo)
2. Autentica en la API y ejecuta todos los `.graphql` en `queries/graphql/`
3. Guarda los resultados en `output/database/` y `output/api/`

**Prerequisitos:** VPN activa para el paso 1.

---

### Modo 2 — Extracción Individual de API

Ejecuta una sola query GraphQL de forma directa y autónoma.

```bash
# Dimensión de Asuntos (BusinessMeta)
python scripts/extract_dim_asuntos.py

# Dimensión de Usuarios (Users)
python scripts/extract_dim_usuarios.py

# Hechos de Tiempos (TimesByFiltersPaged)
python scripts/extract_hechos_tiempos.py
```

**Qué hacen:** Autenticación → paginación automática → CSV en `output/api/`.

**Sin prerequisitos:** No requieren VPN.

---

### Modo 3 — Extractor Automático de API (módulo)

Ejecuta todos los queries GraphQL en `queries/graphql/` de forma automática.

```bash
python -m src.extractors.api_extractor
# o bien:
python src/extractors/api_extractor.py
```

**Qué hace:** Igual que `extract_all.py` pero solo la parte de API.

---

### Modo 4 — Extractor de Base de Datos (módulo)

Ejecuta todos los queries SQL en `queries/sql/` recursivamente.

```bash
python -m src.extractors.database_extractor
# o bien:
python src/extractors/database_extractor.py
```

**Prerequisitos:** VPN activa.

---

### Modo 5 — Extractor Interactivo de API

Muestra un menú para seleccionar qué query GraphQL ejecutar. Permite ejecutar múltiples queries en la misma sesión.

```bash
python -m src.extractors.interactive_api_extractor
# o bien:
python src/extractors/interactive_api_extractor.py
```

**Flujo del menú:**
```
════════════════════════════════════════════════════════════════════════════════
MENÚ DE QUERIES GRAPHQL
════════════════════════════════════════════════════════════════════════════════

Queries disponibles:

  1. dim_asuntos.graphql
  2. dim_usuarios.graphql
  3. hechos_tiempos.graphql
  0. Salir

════════════════════════════════════════════════════════════════════════════════

Selecciona el número del query que deseas ejecutar: _
```

Después de ejecutar un query, pregunta si se desea ejecutar otro. Guarda tanto el JSON crudo como el CSV en `output/api/`.

---

### Modo 6 — Reporte Diario con Telegram

Ejecuta todas las extracciones y envía un reporte HTML detallado al chat de Telegram configurado.

**Opción A — Script Python directo:**
```bash
python scripts/run_daily_report.py
```

**Opción B — Shell script (Linux/Mac):**
```bash
bash scripts/run_report.sh
```

**Opción C — Batch script (Windows):**
```cmd
scripts\run_report.bat
```

**Qué hace:**
1. Ejecuta `database_extractor` + `api_extractor`
2. Recopila estadísticas de todos los CSVs generados (filas y tamaño)
3. Formatea y envía un mensaje HTML a Telegram con el resumen

**Ejemplo de mensaje Telegram:**
```
✅ REPORTE DIARIO DE EXTRACCIÓN

📅 Fecha: 2025-05-23 23:00:15
🔔 Estado: EXITOSO

📊 EXTRACCIÓN DESDE BASE DE DATOS
• Total de registros: 12,450
• Tamaño total: 2.34 MB
• Archivos generados: 4

  • dim_asuntos.csv
    └ Registros: 1,230 | Tamaño: 450.00 KB
  ...

🌐 EXTRACCIÓN DESDE API
• Total de registros: 8,900
...

📈 RESUMEN TOTAL
• Total de registros: 21,350
• Tamaño total: 5.12 MB
• Archivos generados: 7
```

---

### Modo 7 — Demonio de Ejecución Automática

Proceso continuo que espera hasta las 23:00 y ejecuta el reporte diario automáticamente. Alternativa a cron/Task Scheduler que no requiere configuración de sistema.

```bash
python scripts/run_daemon.py
```

**Comportamiento:**
- Calcula cuántos segundos faltan para las 23:00.
- Duerme hasta esa hora.
- Ejecuta `daily_report.main()`.
- Reprograma para el día siguiente y repite infinitamente.
- Se detiene con `Ctrl+C`.

```
============================================================
🚀 INICIANDO DEMONIO DE REPORTE DIARIO
============================================================
El script se ejecutará todos los días a las 23:00
Mantén esta ventana abierta para que el proceso continúe.
============================================================

[10:30:00] Próxima ejecución: 2025-05-23 23:00:00
Esperando 12.50 horas...
```

---

## Scripts de Automatización

### Configurar Cron Job (Linux/Mac)

Configura el cron job del sistema para ejecutar el reporte diario a las 23:00.

```bash
bash scripts/setup_cron.sh
```

**Qué hace:**
1. Detecta la ruta de `python3` y del proyecto.
2. Muestra la configuración propuesta y pide confirmación.
3. Agrega la entrada a `crontab` (o reemplaza si ya existe).
4. Crea la carpeta `logs/` para los archivos de log.

**Entrada de cron generada:**
```
0 23 * * * cd /ruta/al/proyecto && python3 scripts/daily_report.py >> logs/daily_report.log 2>&1
```

**Comandos útiles post-instalación:**
```bash
# Ver tareas programadas
crontab -l

# Editar o eliminar tareas
crontab -e
```

---

### Configurar Task Scheduler (Windows)

Configura el Programador de Tareas de Windows para ejecutar el reporte diario a las 23:00.

```powershell
# Ejecutar como Administrador
.\scripts\setup_cron_windows.ps1
```

**Prerrequisito:** PowerShell ejecutado como Administrador.

**Qué hace:**
1. Detecta `python.exe` en el PATH.
2. Muestra la configuración propuesta y pide confirmación.
3. Registra la tarea `Datawarehouse_Daily_Report` en el Task Scheduler.

**Configuración de la tarea:**
- Nombre: `Datawarehouse_Daily_Report`
- Disparador: Diariamente a las 23:00
- Acción: `python.exe scripts\daily_report.py`
- Directorio: raíz del proyecto
- Nivel: Mayor privilegio

**Comandos útiles post-instalación:**
```powershell
# Ver la tarea
Get-ScheduledTask -TaskName "Datawarehouse_Daily_Report"

# Ejecutar manualmente
Start-ScheduledTask -TaskName "Datawarehouse_Daily_Report"

# Eliminar la tarea
Unregister-ScheduledTask -TaskName "Datawarehouse_Daily_Report" -Confirm:$false
```

---

## Tabla Resumen de Scripts

| Script | Modo | VPN | Telegram | Interactivo |
|--------|------|-----|----------|-------------|
| `extract_all.py` | BD + API | Requerida | No | No |
| `extract_dim_asuntos.py` | Solo API | No | No | No |
| `extract_dim_usuarios.py` | Solo API | No | No | No |
| `extract_hechos_tiempos.py` | Solo API | No | No | No |
| `src.extractors.api_extractor` | Solo API | No | No | No |
| `src.extractors.database_extractor` | Solo BD | Requerida | No | No |
| `src.extractors.interactive_api_extractor` | API menú | No | No | **Sí** |
| `run_daily_report.py` | BD + API + Telegram | Requerida | **Sí** | No |
| `run_report.sh` | BD + API + Telegram | Requerida | **Sí** | No |
| `run_report.bat` | BD + API + Telegram | Requerida | **Sí** | No |
| `run_daemon.py` | BD + API + Telegram (23:00) | Requerida | **Sí** | No |
| `setup_cron.sh` | Configura cron | — | — | **Sí** |
| `setup_cron_windows.ps1` | Configura Task Scheduler | — | — | **Sí** |

---

## Archivos de Salida Generados

| Script / Extractor | Directorio | Archivos |
|-------------------|-----------|---------|
| `database_extractor` | `output/database/` | `dim_asuntos.csv`, `dim_usuarios.csv`, `hechos_tiempos.csv`, `hechos_capacidad.csv`, `hechos_estado_resultados.csv` |
| `api_extractor` / individuales | `output/api/` | `dim_asuntos.csv`, `dim_usuarios.csv`, `hechos_tiempos.csv` |
| `interactive_api_extractor` | `output/api/` | `<query_name>.csv` + `<query_name>.json` |

---

## Cómo Agregar un Nuevo Extractor

### Para una nueva consulta SQL:

1. Crear el archivo en `queries/sql/dimensions/` o `queries/sql/facts/`:
   ```sql
   -- queries/sql/facts/hechos_nuevo.sql
   SELECT ... FROM tabla WHERE ...
   ```
2. El `database_extractor` lo ejecutará automáticamente en la próxima corrida.

### Para un nuevo query GraphQL automático:

1. Crear el query en `queries/graphql/`:
   ```graphql
   # queries/graphql/nuevo_query.graphql
   query NuevoQuery($page: Int, $limit: Int) { ... }
   ```
2. Crear el archivo de variables (puede estar vacío):
   ```json
   // queries/graphql/nuevo_query.variables.json
   { "page": 1, "limit": 1000 }
   ```
3. Si el query tiene un tipo de paginación no reconocido, agregar soporte en `src/api/pagination.py` y `src/utils/graphql_parser.py`.
4. (Opcional) Crear un script individual en `scripts/extract_nuevo_query.py` siguiendo el patrón de los existentes.
