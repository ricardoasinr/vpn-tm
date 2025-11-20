"""Utilidades para escribir archivos CSV"""
import csv
from pathlib import Path
from typing import List, Dict, Any


def write_csv(data: List[Dict[str, Any]], output_file: Path, fieldnames: List[str] = None):
    """
    Escribe datos a un archivo CSV.
    
    Args:
        data: Lista de diccionarios con los datos
        output_file: Ruta del archivo CSV de salida
        fieldnames: Lista de nombres de columnas (si None, se infieren de los datos)
    """
    if not data:
        return
    
    if fieldnames is None:
        # Obtener todas las columnas posibles (unión de todas las claves)
        all_columns = set()
        for row in data:
            all_columns.update(row.keys())
        fieldnames = sorted(list(all_columns))
    
    # Crear directorio si no existe
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Escribir CSV
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(data)

