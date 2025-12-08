#!/bin/bash
#
# Script simple para ejecutar el reporte diario manualmente
# Ejecuta todas las extracciones y envía el reporte por Telegram inmediatamente
#

# Obtener el directorio del script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

# Cambiar al directorio del proyecto
cd "$PROJECT_ROOT"

# Ejecutar el script de Python
python3 scripts/run_daily_report.py

