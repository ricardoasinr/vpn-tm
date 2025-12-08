#!/usr/bin/env python3
"""
Script para ejecutar manualmente el reporte diario.
Ejecuta todas las extracciones y envía el reporte por Telegram inmediatamente.
No requiere esperar al cron job.
"""
import sys
import os
from pathlib import Path

# Obtener el directorio del script y el proyecto
script_dir = Path(__file__).parent
project_root = script_dir.parent

# Cambiar al directorio del proyecto para asegurar paths relativos
os.chdir(project_root)

# Agregar el directorio raíz al path
sys.path.insert(0, str(project_root))

# Importar y ejecutar el reporte diario
if __name__ == "__main__":
    print("\n" + "="*80)
    print("🚀 EJECUTANDO REPORTE DIARIO MANUALMENTE")
    print("="*80)
    print("Este script ejecuta todas las extracciones y envía el reporte por Telegram")
    print("No es necesario esperar al cron job programado.\n")
    print("="*80 + "\n")
    
    # Ejecutar el módulo daily_report
    from scripts import daily_report
    daily_report.main()

