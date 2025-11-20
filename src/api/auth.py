"""Módulo de autenticación de la API"""
import sys
import json
import requests
from pathlib import Path
from typing import Optional

# Agregar el directorio raíz al path para importar config
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from config.api import API_CONFIG


def login() -> Optional[str]:
    """
    Hace login y retorna el bearer token.
    """
    print("="*70)
    print("Haciendo login...")
    print("="*70)
    
    url = f"{API_CONFIG['base_url']}{API_CONFIG['auth_endpoint']}"
    
    headers = {
        'tenant-name': API_CONFIG['tenant_name'],
        'Origin': API_CONFIG['origin'],
        'Content-Type': 'application/json'
    }
    
    data = {
        "username": API_CONFIG['username'],
        "password": API_CONFIG['password']
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        
        result = response.json()
        
        # El token puede estar en diferentes campos según la respuesta
        if 'token' in result:
            token = result['token']
        elif 'access_token' in result:
            token = result['access_token']
        elif 'accessToken' in result:
            token = result['accessToken']
        else:
            token_str = json.dumps(result)
            print(f"Respuesta del login: {token_str[:200]}...")
            raise ValueError("No se encontró el token en la respuesta del login")
        
        print(f"✓ Login exitoso. Token obtenido: {token[:50]}...")
        return token
        
    except requests.exceptions.RequestException as e:
        print(f"✗ ERROR al hacer login: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"  Respuesta: {e.response.text[:200]}")
        return None
    except Exception as e:
        print(f"✗ ERROR inesperado en login: {e}")
        return None

