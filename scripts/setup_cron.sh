#!/bin/bash
#
# Script helper para configurar el cron job que ejecuta el reporte diario
# a las 23:00
#

# Obtener el directorio del script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"
PYTHON_PATH=$(which python3)

# Verificar que python3 esté disponible
if [ -z "$PYTHON_PATH" ]; then
    echo "❌ Error: python3 no se encuentra en el PATH"
    echo "   Por favor, instala Python 3 o actualiza tu PATH"
    exit 1
fi

# Ruta completa al script de reporte diario
DAILY_REPORT_SCRIPT="$PROJECT_ROOT/scripts/daily_report.py"

# Verificar que el script existe
if [ ! -f "$DAILY_REPORT_SCRIPT" ]; then
    echo "❌ Error: No se encuentra el script daily_report.py"
    echo "   Ruta esperada: $DAILY_REPORT_SCRIPT"
    exit 1
fi

# Crear el comando de cron
# 0 23 * * * = cada día a las 23:00
CRON_CMD="0 23 * * * cd $PROJECT_ROOT && $PYTHON_PATH $DAILY_REPORT_SCRIPT >> $PROJECT_ROOT/logs/daily_report.log 2>&1"

# Crear directorio de logs si no existe
mkdir -p "$PROJECT_ROOT/logs"

echo "════════════════════════════════════════════════════════════"
echo "  CONFIGURACIÓN DE CRON JOB PARA REPORTE DIARIO"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "📁 Directorio del proyecto: $PROJECT_ROOT"
echo "🐍 Python: $PYTHON_PATH"
echo "📄 Script: $DAILY_REPORT_SCRIPT"
echo ""
echo "⏰ El cron job se ejecutará diariamente a las 23:00"
echo "📝 Los logs se guardarán en: $PROJECT_ROOT/logs/daily_report.log"
echo ""
echo "════════════════════════════════════════════════════════════"
echo ""
echo "¿Deseas agregar esta tarea al crontab? (s/n)"
read -r response

if [[ "$response" =~ ^[sS][iI]?$ ]]; then
    # Verificar si ya existe una entrada similar
    if crontab -l 2>/dev/null | grep -q "daily_report.py"; then
        echo ""
        echo "⚠️  Ya existe una entrada en crontab para daily_report.py"
        echo "¿Deseas reemplazarla? (s/n)"
        read -r replace_response
        
        if [[ "$replace_response" =~ ^[sS][iI]?$ ]]; then
            # Eliminar entrada existente
            crontab -l 2>/dev/null | grep -v "daily_report.py" | crontab -
            echo "✓ Entrada existente eliminada"
        else
            echo "❌ Operación cancelada"
            exit 0
        fi
    fi
    
    # Agregar nueva entrada
    (crontab -l 2>/dev/null; echo "$CRON_CMD") | crontab -
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "✅ Cron job agregado exitosamente"
        echo ""
        echo "Para ver tus tareas cron programadas, ejecuta:"
        echo "  crontab -l"
        echo ""
        echo "Para eliminar esta tarea, ejecuta:"
        echo "  crontab -e"
        echo ""
        echo "O ejecuta este script nuevamente y elige reemplazar"
    else
        echo ""
        echo "❌ Error al agregar el cron job"
        exit 1
    fi
else
    echo ""
    echo "ℹ️  Para agregarlo manualmente, ejecuta:"
    echo "  crontab -e"
    echo ""
    echo "Y agrega esta línea:"
    echo "  $CRON_CMD"
    echo ""
fi

