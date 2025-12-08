"""Módulo para enviar mensajes por Telegram"""
import sys
import requests
from pathlib import Path
from typing import Optional

# Agregar el directorio raíz al path para importar config
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from config.telegram import TELEGRAM_CONFIG


def send_telegram_message(message: str) -> bool:
    """
    Envía un mensaje por Telegram
    
    Args:
        message: Mensaje a enviar (puede incluir HTML)
        
    Returns:
        True si se envió correctamente, False en caso contrario
    """
    bot_token = TELEGRAM_CONFIG['bot_token']
    chat_id = TELEGRAM_CONFIG['chat_id']
    
    if not bot_token or not chat_id:
        print("❌ Error: TELEGRAM_BOT_TOKEN o TELEGRAM_CHAT_ID no están configurados")
        return False
    
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    
    payload = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'HTML',
        'disable_web_page_preview': True
    }
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        print("✓ Mensaje enviado por Telegram")
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ Error al enviar mensaje por Telegram: {e}")
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_detail = e.response.json()
                print(f"  Detalle: {error_detail}")
            except:
                print(f"  Respuesta: {e.response.text[:200]}")
        return False
    except Exception as e:
        print(f"❌ Error inesperado al enviar mensaje por Telegram: {e}")
        return False

