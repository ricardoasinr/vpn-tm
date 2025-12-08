"""Configuración de Telegram"""
import os

# Intentar cargar variables de entorno desde .env si existe
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # Si python-dotenv no está instalado, continuar sin él
    pass

TELEGRAM_CONFIG = {
    'bot_token': os.getenv('TELEGRAM_BOT_TOKEN', '8408123350:AAF12RcImqRDKE3JcvMbiw0tA5evd-S_ohw'),
    'chat_id': os.getenv('TELEGRAM_CHAT_ID', '6340306003')
}

