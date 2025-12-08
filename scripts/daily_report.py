#!/usr/bin/env python3
"""
Script para ejecutar extracciones diarias y enviar reporte por Telegram.
Ejecuta todos los extractores y envía un reporte detallado con estadísticas.
"""
import sys
import csv
import io
import traceback
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.extractors.database_extractor import main as extract_database
from src.extractors.api_extractor import main as extract_api
from src.utils.telegram_sender import send_telegram_message


def count_csv_rows(csv_path: Path) -> int:
    """
    Cuenta el número de filas en un archivo CSV (sin contar el encabezado)
    
    Args:
        csv_path: Ruta al archivo CSV
        
    Returns:
        Número de filas (sin encabezado), -1 si hay error
    """
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            # Saltar encabezado
            next(reader, None)
            row_count = sum(1 for _ in reader)
            return row_count
    except Exception as e:
        print(f"  ⚠ Error al contar filas en {csv_path.name}: {e}")
        return -1


def format_file_size(size_bytes: int) -> str:
    """
    Formatea el tamaño de archivo en formato legible
    
    Args:
        size_bytes: Tamaño en bytes
        
    Returns:
        String formateado (ej: "1.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"


def get_file_stats(directory: Path) -> Dict[str, Dict]:
    """
    Obtiene estadísticas de archivos CSV en un directorio
    
    Args:
        directory: Directorio donde buscar archivos CSV
        
    Returns:
        Diccionario con estadísticas: {filename: {'rows': int, 'size': int, 'size_formatted': str}}
    """
    stats = {}
    
    if not directory.exists():
        return stats
    
    for csv_file in directory.glob("*.csv"):
        rows = count_csv_rows(csv_file)
        size = csv_file.stat().st_size
        stats[csv_file.name] = {
            'rows': rows,
            'size': size,
            'size_formatted': format_file_size(size)
        }
    
    return stats


def execute_extractors() -> Tuple[bool, List[str]]:
    """
    Ejecuta todos los extractores y captura errores
    
    Returns:
        Tupla (success: bool, errors: List[str])
    """
    errors = []
    success = True
    
    # Ejecutar extractor de base de datos
    print("\n" + "="*70)
    print("Ejecutando extracción desde base de datos...")
    print("="*70)
    try:
        extract_database()
    except Exception as e:
        error_msg = f"Error en extracción de base de datos: {str(e)}"
        errors.append(error_msg)
        print(f"✗ {error_msg}")
        traceback.print_exc()
        success = False
    
    # Ejecutar extractor de API
    print("\n" + "="*70)
    print("Ejecutando extracción desde API...")
    print("="*70)
    try:
        extract_api()
    except Exception as e:
        error_msg = f"Error en extracción de API: {str(e)}"
        errors.append(error_msg)
        print(f"✗ {error_msg}")
        traceback.print_exc()
        success = False
    
    return success, errors


def format_telegram_message(
    db_stats: Dict[str, Dict],
    api_stats: Dict[str, Dict],
    execution_time: datetime,
    success: bool,
    errors: List[str]
) -> str:
    """
    Formatea el mensaje de Telegram con HTML
    
    Args:
        db_stats: Estadísticas de archivos de base de datos
        api_stats: Estadísticas de archivos de API
        execution_time: Timestamp de ejecución
        success: Si la ejecución fue exitosa
        errors: Lista de errores si los hay
        
    Returns:
        Mensaje formateado en HTML
    """
    # Encabezado
    status_icon = "✅" if success else "⚠️"
    status_text = "EXITOSO" if success else "CON ERRORES"
    
    msg = f"{status_icon} <b>REPORTE DIARIO DE EXTRACCIÓN</b>\n\n"
    msg += f"📅 <b>Fecha:</b> {execution_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
    msg += f"🔔 <b>Estado:</b> {status_text}\n\n"
    
    # Resumen de base de datos
    msg += "<b>📊 EXTRACCIÓN DESDE BASE DE DATOS</b>\n"
    if db_stats:
        total_rows_db = sum(s['rows'] for s in db_stats.values() if s['rows'] >= 0)
        total_size_db = sum(s['size'] for s in db_stats.values())
        
        msg += f"• Total de registros: <code>{total_rows_db:,}</code>\n"
        msg += f"• Tamaño total: <code>{format_file_size(total_size_db)}</code>\n"
        msg += f"• Archivos generados: <code>{len(db_stats)}</code>\n\n"
        
        msg += "<i>Detalle por archivo:</i>\n"
        for filename, stats in sorted(db_stats.items()):
            rows_str = f"{stats['rows']:,}" if stats['rows'] >= 0 else "Error"
            msg += f"  • {filename}\n"
            msg += f"    └ Registros: <code>{rows_str}</code> | Tamaño: <code>{stats['size_formatted']}</code>\n"
    else:
        msg += "⚠️ No se encontraron archivos CSV\n"
    msg += "\n"
    
    # Resumen de API
    msg += "<b>🌐 EXTRACCIÓN DESDE API</b>\n"
    if api_stats:
        total_rows_api = sum(s['rows'] for s in api_stats.values() if s['rows'] >= 0)
        total_size_api = sum(s['size'] for s in api_stats.values())
        
        msg += f"• Total de registros: <code>{total_rows_api:,}</code>\n"
        msg += f"• Tamaño total: <code>{format_file_size(total_size_api)}</code>\n"
        msg += f"• Archivos generados: <code>{len(api_stats)}</code>\n\n"
        
        msg += "<i>Detalle por archivo:</i>\n"
        for filename, stats in sorted(api_stats.items()):
            rows_str = f"{stats['rows']:,}" if stats['rows'] >= 0 else "Error"
            msg += f"  • {filename}\n"
            msg += f"    └ Registros: <code>{rows_str}</code> | Tamaño: <code>{stats['size_formatted']}</code>\n"
    else:
        msg += "⚠️ No se encontraron archivos CSV\n"
    msg += "\n"
    
    # Resumen total
    all_stats = {**db_stats, **api_stats}
    if all_stats:
        total_rows_all = sum(s['rows'] for s in all_stats.values() if s['rows'] >= 0)
        total_size_all = sum(s['size'] for s in all_stats.values())
        
        msg += "<b>📈 RESUMEN TOTAL</b>\n"
        msg += f"• Total de registros: <code>{total_rows_all:,}</code>\n"
        msg += f"• Tamaño total: <code>{format_file_size(total_size_all)}</code>\n"
        msg += f"• Archivos generados: <code>{len(all_stats)}</code>\n\n"
    
    # Errores
    if errors:
        msg += "<b>❌ ERRORES ENCONTRADOS</b>\n"
        for i, error in enumerate(errors, 1):
            msg += f"{i}. {error}\n"
        msg += "\n"
    
    # Pie de mensaje
    msg += "ℹ️ <i>Reporte generado automáticamente por el sistema de extracción</i>"
    
    return msg


def main():
    """Función principal"""
    execution_time = datetime.now()
    project_root = Path(__file__).parent.parent
    
    print("\n" + "="*70)
    print("INICIANDO REPORTE DIARIO DE EXTRACCIÓN")
    print("="*70)
    print(f"Fecha/Hora: {execution_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    # Ejecutar extractores
    success, errors = execute_extractors()
    
    # Obtener estadísticas de archivos generados
    print("\n" + "="*70)
    print("Recopilando estadísticas de archivos generados...")
    print("="*70)
    
    db_output_dir = project_root / "output" / "database"
    api_output_dir = project_root / "output" / "api"
    
    db_stats = get_file_stats(db_output_dir)
    api_stats = get_file_stats(api_output_dir)
    
    print(f"\nArchivos de BD encontrados: {len(db_stats)}")
    for filename in db_stats.keys():
        print(f"  • {filename}")
    
    print(f"\nArchivos de API encontrados: {len(api_stats)}")
    for filename in api_stats.keys():
        print(f"  • {filename}")
    
    # Formatear y enviar mensaje
    message = format_telegram_message(
        db_stats=db_stats,
        api_stats=api_stats,
        execution_time=execution_time,
        success=success,
        errors=errors
    )
    
    print("\n" + "="*70)
    print("Enviando reporte por Telegram...")
    print("="*70)
    
    if send_telegram_message(message):
        print("\n✅ Reporte enviado exitosamente")
    else:
        print("\n❌ Error al enviar reporte por Telegram")
        # Si falla el envío, mostrar el mensaje en consola
        print("\n" + "="*70)
        print("CONTENIDO DEL REPORTE (no se pudo enviar por Telegram):")
        print("="*70)
        print(message.replace('<b>', '').replace('</b>', '').replace('<code>', '').replace('</code>', '')
              .replace('<i>', '').replace('</i>', '').replace('└', '  '))
    
    print("\n" + "="*70)
    print("PROCESO COMPLETADO")
    print("="*70)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Proceso interrumpido por el usuario")
        sys.exit(1)
    except Exception as e:
        error_msg = f"Error fatal: {str(e)}"
        print(f"\n❌ {error_msg}")
        traceback.print_exc()
        
        # Intentar enviar error crítico por Telegram
        critical_message = (
            f"🚨 <b>ERROR CRÍTICO EN REPORTE DIARIO</b>\n\n"
            f"⚠️ El proceso de extracción diaria falló con un error crítico.\n\n"
            f"<b>Error:</b> {str(e)}\n"
            f"<b>Fecha:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            f"Por favor, revisa los logs del sistema."
        )
        send_telegram_message(critical_message)
        sys.exit(1)

