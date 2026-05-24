# Automatización y Programación de Tareas

El sistema ofrece tres métodos para ejecutar el reporte diario de forma automática a las 23:00.

---

## Método 1 — Demonio Python

El demonio es un proceso Python que se ejecuta indefinidamente en primer plano y lanza el reporte a las 23:00 cada día. No requiere configuración de sistema operativo.

```bash
python scripts/run_daemon.py
```

**Ventajas:**
- Sin configuración de sistema operativo.
- Funciona igual en Linux, Mac y Windows.
- Fácil de monitorear (imprime en consola).

**Desventajas:**
- Requiere mantener la terminal/ventana abierta.
- Se detiene si el proceso es interrumpido.

**Comportamiento:**
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

**Para detenerlo:** `Ctrl+C`

---

## Método 2 — Cron Job (Linux/Mac)

Configura el cron job del sistema operativo para ejecutar el reporte automáticamente.

### Instalación automática

```bash
bash scripts/setup_cron.sh
```

El script:
1. Detecta rutas automáticamente.
2. Muestra la configuración y pide confirmación.
3. Agrega la entrada al crontab del usuario actual.
4. Crea la carpeta `logs/` para persistir los logs.

### Instalación manual

```bash
crontab -e
```

Agregar esta línea (ajustar las rutas):
```cron
0 23 * * * cd /ruta/al/proyecto && python3 scripts/daily_report.py >> /ruta/al/proyecto/logs/daily_report.log 2>&1
```

### Verificar que está activo

```bash
crontab -l
```

### Ver logs en tiempo real

```bash
tail -f logs/daily_report.log
```

### Eliminar el cron job

```bash
crontab -e
# Borrar la línea correspondiente
```

---

## Método 3 — Task Scheduler (Windows)

Configura el Programador de Tareas de Windows para ejecutar el reporte automáticamente.

### Instalación automática

Abrir PowerShell **como Administrador** y ejecutar:

```powershell
.\scripts\setup_cron_windows.ps1
```

El script:
1. Valida que se ejecuta con privilegios de administrador.
2. Detecta `python.exe` y las rutas del proyecto.
3. Muestra la configuración y pide confirmación.
4. Crea la tarea `Datawarehouse_Daily_Report` en el Task Scheduler.

### Instalación manual (GUI)

1. Abrir **Programador de tareas** (`taskschd.msc`)
2. **Crear tarea básica**
3. Nombre: `Datawarehouse_Daily_Report`
4. Desencadenador: **Diariamente** a las **23:00**
5. Acción: **Iniciar un programa**
   - Programa: `C:\ruta\a\python.exe`
   - Argumentos: `"C:\ruta\al\proyecto\scripts\daily_report.py"`
   - Iniciar en: `C:\ruta\al\proyecto\`

### Comandos PowerShell útiles

```powershell
# Ver la tarea
Get-ScheduledTask -TaskName "Datawarehouse_Daily_Report"

# Ejecutar manualmente ahora
Start-ScheduledTask -TaskName "Datawarehouse_Daily_Report"

# Ver historial de ejecuciones
Get-ScheduledTaskInfo -TaskName "Datawarehouse_Daily_Report"

# Deshabilitar temporalmente
Disable-ScheduledTask -TaskName "Datawarehouse_Daily_Report"

# Habilitar de nuevo
Enable-ScheduledTask -TaskName "Datawarehouse_Daily_Report"

# Eliminar
Unregister-ScheduledTask -TaskName "Datawarehouse_Daily_Report" -Confirm:$false
```

---

## Ejecución Manual del Reporte

Para ejecutar el reporte diario en cualquier momento (sin esperar la hora programada):

**Linux/Mac:**
```bash
bash scripts/run_report.sh
# o
python scripts/run_daily_report.py
```

**Windows:**
```cmd
scripts\run_report.bat
```
```powershell
python scripts\run_daily_report.py
```

---

## Flujo Completo del Reporte Diario

```
scripts/daily_report.py
         │
         ├─── 1. extract_database()
         │         └─── Conecta a Aurora MySQL (VPN requerida)
         │              Ejecuta queries/sql/**/*.sql
         │              Guarda CSVs en output/database/
         │
         ├─── 2. extract_api()
         │         └─── POST /api/auth/token → JWT token
         │              Para cada queries/graphql/*.graphql:
         │                  POST /graphql/ página 1...N
         │              Guarda CSVs en output/api/
         │
         ├─── 3. get_file_stats(output/database/)
         │         └─── Cuenta filas y calcula tamaño de cada CSV
         │
         ├─── 4. get_file_stats(output/api/)
         │
         ├─── 5. format_telegram_message()
         │         └─── Genera HTML con estadísticas
         │
         └─── 6. send_telegram_message()
                   └─── POST https://api.telegram.org/bot{token}/sendMessage
```

---

## Manejo de Errores en el Reporte Diario

El reporte incluye manejo de errores en varios niveles:

| Escenario | Comportamiento |
|-----------|---------------|
| Error en extracción de BD | Captura el error, continúa con la extracción de API, reporta el error en Telegram |
| Error en extracción de API | Captura el error, continúa, reporta en Telegram |
| Error al enviar a Telegram | Imprime el reporte completo en la consola como fallback |
| Error fatal (excepción no capturada) | Intenta enviar notificación de error crítico a Telegram y sale con código 1 |

El mensaje de Telegram muestra el estado final:
- `✅ EXITOSO` — ambas extracciones completadas sin errores
- `⚠️ CON ERRORES` — al menos una extracción falló, con detalle de errores al final del mensaje

---

## Estructura de Logs

Cuando se usa cron o el script `run_report.sh`, los logs se guardan en:

```
logs/
└── daily_report.log    # stdout + stderr del script
```

La carpeta `logs/` se crea automáticamente por `setup_cron.sh`. Para revisarla:

```bash
# Ver las últimas 100 líneas
tail -n 100 logs/daily_report.log

# Seguir en tiempo real
tail -f logs/daily_report.log

# Buscar errores
grep "ERROR\|✗\|❌" logs/daily_report.log
```
