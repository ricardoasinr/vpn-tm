"""Cliente GraphQL para la API"""
import sys
import requests
from pathlib import Path
from typing import Dict, Any, List, Optional

# Agregar el directorio raíz al path para importar config
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from config.api import API_CONFIG
from src.api.pagination import has_next_page


def graphql_request(token: str, query: str, variables: Dict[str, Any], 
                    query_name: str, paginate: bool = True) -> Optional[List[Dict[str, Any]]]:
    """
    Ejecuta un request GraphQL usando el token de autenticación.
    Maneja paginación automáticamente si está habilitada.
    
    Args:
        token: Bearer token para autenticación
        query: Query GraphQL
        variables: Variables para el query
        query_name: Nombre del query (para logging)
        paginate: Si True, recorre todas las páginas automáticamente
    
    Returns:
        Lista de todas las respuestas de todas las páginas o None si hay error
    """
    print(f"\nEjecutando query: {query_name}...")
    
    url = f"{API_CONFIG['base_url']}{API_CONFIG['graphql_endpoint']}"
    
    headers = {
        'tenant-name': API_CONFIG['tenant_name'],
        'Origin': API_CONFIG['origin'],
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}',
        'Accept-Language': 'es-419,es;q=0.9',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Pragma': 'no-cache',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36',
        'accept': '*/*'
    }
    
    all_results = []
    current_page = variables.get('page', 1) if isinstance(variables.get('page'), int) else 1
    
    while True:
        # Actualizar variables con la página actual
        current_variables = variables.copy()
        current_variables['page'] = current_page
        
        payload = {
            "query": query,
            "variables": current_variables
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            
            # Verificar errores de GraphQL
            if 'errors' in result:
                print(f"✗ ERROR en query GraphQL {query_name}:")
                for error in result['errors']:
                    print(f"  {error}")
                return None
            
            all_results.append(result)
            
            # Verificar si hay más páginas
            if not paginate:
                break
            
            data_obj = result.get('data', {})
            has_next, total, current_total = has_next_page(data_obj)
            
            if current_total > 0:
                print(f"  Página {current_page}: {current_total} registros (Total: {total})")
            
            if not has_next:
                break
            
            current_page += 1
            
        except requests.exceptions.RequestException as e:
            print(f"✗ ERROR al ejecutar query {query_name} (página {current_page}): {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"  Respuesta: {e.response.text[:200]}")
            return None
        except Exception as e:
            print(f"✗ ERROR inesperado en query {query_name} (página {current_page}): {e}")
            return None
    
    print(f"✓ Query {query_name} ejecutado exitosamente ({len(all_results)} página(s))")
    return all_results

