@echo off
REM Script simple para ejecutar el reporte diario manualmente en Windows
REM Ejecuta todas las extracciones y envia el reporte por Telegram inmediatamente

REM Obtener el directorio del script
set SCRIPT_DIR=%~dp0
set PROJECT_ROOT=%SCRIPT_DIR%\..

REM Cambiar al directorio del proyecto
cd /d "%PROJECT_ROOT%"

REM Ejecutar el script de Python
python scripts\run_daily_report.py

REM Mantener la ventana abierta para ver el resultado
pause

