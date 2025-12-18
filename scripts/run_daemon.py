#!/usr/bin/env python3
"""
Script demonio que se ejecuta infinitamente y lanza el reporte diario a las 23:00.
Alternativa a cron (Linux) o Task Scheduler (Windows).
"""
import time
import sys
import os
from datetime import datetime, timedelta
from pathlib import Path

# Configurar paths
script_dir = Path(__file__).parent
project_root = script_dir.parent

# Asegurar que estamos en el directorio raíz del proyecto
os.chdir(project_root)
sys.path.insert(0, str(project_root))

# Importar el módulo de reporte
try:
    from scripts import daily_report
except ImportError:
    # Si falla la importación directa, intentar agregar el directorio actual al path
    sys.path.insert(0, str(script_dir))
    import daily_report

def get_seconds_until_target(target_hour, target_minute):
    now = datetime.now()
    target = now.replace(hour=target_hour, minute=target_minute, second=0, microsecond=0)
    
    if now >= target:
        # Si ya pasó la hora hoy, programar para mañana
        target += timedelta(days=1)
        
    return (target - now).total_seconds()

def main():
    TARGET_HOUR = 23
    TARGET_MINUTE = 0
    
    print("\n" + "="*60)
    print("🚀 INICIANDO DEMONIO DE REPORTE DIARIO")
    print("="*60)
    print(f"El script se ejecutará todos los días a las {TARGET_HOUR:02d}:{TARGET_MINUTE:02d}")
    print("Mantén esta ventana abierta para que el proceso continúe.")
    print("="*60 + "\n")
    
    while True:
        seconds_wait = get_seconds_until_target(TARGET_HOUR, TARGET_MINUTE)
        next_run = datetime.now() + timedelta(seconds=seconds_wait)
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Próxima ejecución: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Esperando {seconds_wait/3600:.2f} horas...")
        
        # Dormir hasta la hora programada
        try:
            time.sleep(seconds_wait)
        except KeyboardInterrupt:
            print("\n\n🛑 Demonio detenido por el usuario.")
            break
        
        # Ejecutar reporte
        print("\n" + "="*60)
        print(f"[{datetime.now().strftime('%H:%M:%S')}] EJECUTANDO REPORTE DIARIO...")
        print("="*60)
        
        try:
            daily_report.main()
        except Exception as e:
            print(f"❌ Error ejecutando el reporte: {e}")
        
        print("\n" + "-"*60)
        print("Ejecución finalizada. Reprogramando para mañana...")
        print("-"*60 + "\n")
        
        # Dormir un poco para asegurar que no se ejecute dos veces en el mismo segundo
        time.sleep(60)

if __name__ == "__main__":
    main()
