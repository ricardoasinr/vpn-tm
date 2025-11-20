"""Utilidades para parsear comandos curl"""
import json
import re
from typing import Dict, Any, Optional, Tuple


def parse_curl_command(curl_command: str) -> Optional[Tuple[str, Dict[str, str], Dict[str, Any]]]:
    """
    Parsea un comando curl y extrae URL, headers y data (query GraphQL).
    
    Returns:
        Tuple de (url, headers, data_dict) o None si hay error
    """
    try:
        # Extraer URL
        url_match = re.search(r"--location\s+['\"]([^'\"]+)['\"]", curl_command)
        if not url_match:
            url_match = re.search(r"curl\s+['\"]([^'\"]+)['\"]", curl_command)
        if not url_match:
            return None
        url = url_match.group(1)
        
        # Extraer headers
        headers = {}
        header_pattern = r"--header\s+['\"]([^:]+):\s*([^'\"]+)['\"]"
        for match in re.finditer(header_pattern, curl_command):
            key = match.group(1).strip()
            value = match.group(2).strip()
            headers[key] = value
        
        # Extraer data (query GraphQL)
        data_match = re.search(r"--data\s+['\"](.+)['\"]", curl_command, re.DOTALL)
        if not data_match:
            return None
        
        data_str = data_match.group(1)
        # El JSON en curl tiene \n como caracteres escapados
        # Necesitamos convertirlos a newlines reales para que el query GraphQL sea legible
        # Pero JSON no permite newlines sin escapar, así que necesitamos un enfoque diferente
        # Opción: usar eval() con cuidado o procesar manualmente
        # Mejor: usar ast.literal_eval que es más seguro que eval
        import ast
        try:
            # Primero intentar parsear como JSON normal
            data_dict = json.loads(data_str)
        except json.JSONDecodeError:
            # Si falla, puede ser por los \n. Intentar reemplazar
            # Los \n en el string JSON necesitan estar escapados como \\n
            # Pero en el curl ya están como \n (un solo backslash)
            # Necesitamos escapar los newlines reales que puedan estar
            # La mejor solución: usar eval con el string como Python dict (más permisivo)
            # Pero es inseguro. Mejor: procesar manualmente
            # Reemplazar \n (un backslash + n) con \\n (dos backslashes + n) para JSON válido
            data_str_fixed = data_str.replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t')
            try:
                data_dict = json.loads(data_str_fixed)
            except:
                # Último recurso: usar ast.literal_eval (más permisivo que JSON)
                data_dict = ast.literal_eval(data_str)
        
        return url, headers, data_dict
        
    except Exception as e:
        print(f"Error al parsear comando curl: {e}")
        return None

