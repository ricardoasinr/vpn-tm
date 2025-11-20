"""Utilidades para parsear respuestas GraphQL"""
from typing import Dict, Any, List, Optional


def extract_rows_from_graphql_response(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Extrae las filas de datos de las respuestas GraphQL.
    
    Args:
        results: Lista de respuestas JSON de GraphQL (una por página)
    
    Returns:
        Lista de todas las filas de datos
    """
    all_rows_data = []
    
    # Procesar cada página de resultados
    for data in results:
        rows_data = None
        
        if 'data' in data:
            data_obj = data['data']
            
            # Para BusinessMeta (Dim_Asuntos)
            if 'BusinessMeta' in data_obj:
                business_meta = data_obj['BusinessMeta']
                if 'rows' in business_meta:
                    rows_data = business_meta['rows']
            
            # Para Users (Dim_Usuarios)
            elif 'Users' in data_obj:
                users = data_obj['Users']
                if 'users' in users:
                    rows_data = users['users']
            
            # Para TimesByFiltersPaged (Hechos_Tiempos)
            elif 'TimesByFiltersPaged' in data_obj:
                times_data = data_obj['TimesByFiltersPaged']
                if 'times' in times_data:
                    rows_data = times_data['times']
        
        if rows_data:
            all_rows_data.extend(rows_data)
    
    return all_rows_data

