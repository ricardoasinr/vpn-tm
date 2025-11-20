"""Módulo de paginación para queries GraphQL"""
from typing import Dict, Any, Optional, Tuple


def has_next_page(data_obj: Dict[str, Any]) -> Tuple[bool, int, int]:
    """
    Verifica si hay más páginas en la respuesta GraphQL.
    
    Returns:
        Tuple de (has_next, total, current_count)
    """
    has_next = False
    total = 0
    current_count = 0
    
    # Para BusinessMeta
    if 'BusinessMeta' in data_obj:
        meta = data_obj['BusinessMeta'].get('meta', {})
        has_next = meta.get('hasNextPage', False)
        total = meta.get('total', 0)
        current_count = len(data_obj['BusinessMeta'].get('rows', []))
    
    # Para Users
    elif 'Users' in data_obj:
        meta = data_obj['Users'].get('meta', {})
        has_next = meta.get('hasNextPage', False)
        total = meta.get('total', 0)
        current_count = len(data_obj['Users'].get('users', []))
    
    # Para TimesByFiltersPaged
    elif 'TimesByFiltersPaged' in data_obj:
        times_data = data_obj['TimesByFiltersPaged']
        has_next = times_data.get('has_next_page', False)
        total = times_data.get('total', 0)
        current_count = len(times_data.get('times', []))
    
    return has_next, total, current_count

