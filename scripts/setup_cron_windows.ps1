# setup_cron_windows.ps1
# Script helper para configurar el Task Scheduler que ejecuta el reporte diario
# a la medianoche (Windows Server)

# Verificar que se ejecute como administrador
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "❌ Error: Este script debe ejecutarse como Administrador" -ForegroundColor Red
    Write-Host "   Haz clic derecho en PowerShell y selecciona 'Ejecutar como administrador'"
    exit 1
}

# Obtener el directorio del script
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir

# Buscar Python (probablemente 'python' en Windows, no 'python3')
$PythonPath = Get-Command python -ErrorAction SilentlyContinue
if (-not $PythonPath) {
    Write-Host "❌ Error: python no se encuentra en el PATH" -ForegroundColor Red
    Write-Host "   Por favor, instala Python 3 o actualiza tu PATH"
    exit 1
}
$PythonPath = $PythonPath.Source

# Ruta completa al script de reporte diario
$DailyReportScript = Join-Path $ProjectRoot "scripts\daily_report.py"

# Verificar que el script existe
if (-not (Test-Path $DailyReportScript)) {
    Write-Host "❌ Error: No se encuentra el script daily_report.py" -ForegroundColor Red
    Write-Host "   Ruta esperada: $DailyReportScript"
    exit 1
}

# Crear directorio de logs si no existe
$LogsDir = Join-Path $ProjectRoot "logs"
if (-not (Test-Path $LogsDir)) {
    New-Item -ItemType Directory -Path $LogsDir -Force | Out-Null
}

# Nombre de la tarea programada
$TaskName = "Datawarehouse_Daily_Report"

# Hora de ejecución: medianoche (00:00)
$StartTime = "00:00"

# Para ejecutar cada 5 minutos, descomenta la siguiente línea y comenta la línea anterior:
# $StartTime = (Get-Date).AddMinutes(5).ToString("HH:mm")

# Construir el comando
$LogFile = Join-Path $LogsDir "daily_report.log"
$Action = New-ScheduledTaskAction -Execute $PythonPath -Argument "`"$DailyReportScript`"" -WorkingDirectory $ProjectRoot

# Crear trigger: diariamente a medianoche
$Trigger = New-ScheduledTaskTrigger -Daily -At $StartTime

# Para ejecutar cada 5 minutos, descomenta las siguientes líneas y comenta la línea anterior:
# $Trigger = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(5) -RepetitionInterval (New-TimeSpan -Minutes 5) -RepetitionDuration (New-TimeSpan -Days 365)

# Configuración de la tarea
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
$Principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType Interactive -RunLevel Highest

Write-Host ""
Write-Host "════════════════════════════════════════════════════════════"
Write-Host "  CONFIGURACIÓN DE TASK SCHEDULER PARA REPORTE DIARIO"
Write-Host "════════════════════════════════════════════════════════════"
Write-Host ""
Write-Host "📁 Directorio del proyecto: $ProjectRoot"
Write-Host "🐍 Python: $PythonPath"
Write-Host "📄 Script: $DailyReportScript"
Write-Host ""
Write-Host "⏰ La tarea se ejecutará diariamente a las $StartTime (medianoche)"
Write-Host "📝 Los logs se guardarán en: $LogFile"
Write-Host ""
Write-Host "════════════════════════════════════════════════════════════"
Write-Host ""

# Verificar si la tarea ya existe
$ExistingTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue

if ($ExistingTask) {
    Write-Host "⚠️  Ya existe una tarea programada con el nombre: $TaskName" -ForegroundColor Yellow
    $ReplaceResponse = Read-Host "¿Deseas reemplazarla? (s/n)"
    
    if ($ReplaceResponse -match "^[sS]") {
        Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
        Write-Host "✓ Tarea existente eliminada" -ForegroundColor Green
    } else {
        Write-Host "❌ Operación cancelada" -ForegroundColor Red
        exit 0
    }
}

$ContinueResponse = Read-Host "¿Deseas crear esta tarea programada? (s/n)"

if ($ContinueResponse -match "^[sS]") {
    try {
        # Registrar la tarea
        Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -Principal $Principal -Description "Ejecuta el reporte diario de extracción del datawarehouse y envía notificación por Telegram"
        
        Write-Host ""
        Write-Host "✅ Tarea programada creada exitosamente" -ForegroundColor Green
        Write-Host ""
        Write-Host "Para ver la tarea, ejecuta:" -ForegroundColor Cyan
        Write-Host "  Get-ScheduledTask -TaskName '$TaskName'" -ForegroundColor Gray
        Write-Host ""
        Write-Host "Para eliminar la tarea, ejecuta:" -ForegroundColor Cyan
        Write-Host "  Unregister-ScheduledTask -TaskName '$TaskName' -Confirm:`$false" -ForegroundColor Gray
        Write-Host ""
        Write-Host "O ejecuta este script nuevamente y elige reemplazar" -ForegroundColor Cyan
    } catch {
        Write-Host ""
        Write-Host "❌ Error al crear la tarea programada: $_" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host ""
    Write-Host "ℹ️  Para crear la tarea manualmente:" -ForegroundColor Cyan
    Write-Host "   1. Abre 'Programador de tareas' (Task Scheduler)" -ForegroundColor Gray
    Write-Host "   2. Crea una tarea básica" -ForegroundColor Gray
    Write-Host "   3. Nombre: $TaskName" -ForegroundColor Gray
    Write-Host "   4. Desencadenador: Diariamente a las $StartTime" -ForegroundColor Gray
    Write-Host "   5. Acción: Iniciar un programa" -ForegroundColor Gray
    Write-Host "   6. Programa: $PythonPath" -ForegroundColor Gray
    Write-Host "   7. Argumentos: `"$DailyReportScript`"" -ForegroundColor Gray
    Write-Host "   8. Iniciar en: $ProjectRoot" -ForegroundColor Gray
}

