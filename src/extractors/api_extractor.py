#!/usr/bin/env python3
"""
Extractor automático de datos desde la API GraphQL.
Ejecuta queries GraphQL desde archivos .graphql y guarda los resultados en CSV.
"""
import sys
import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.api.auth import login
from src.api.client import graphql_request
from src.utils.graphql_parser import extract_rows_from_graphql_response
from src.utils.json_flattener import flatten_dict
from src.utils.csv_writer import write_csv

# Directorio donde están los queries GraphQL
GRAPHQL_DIR = Path('queries/graphql')
RESULTS_DIR = Path('output/api')


def load_graphql_query(query_file: Path) -> Optional[Tuple[str, Dict[str, Any]]]:
    """
    Lee un query GraphQL y sus variables.
    
    Returns:
        Tuple de (query, variables) o None si hay error
    """
    try:
        # Leer el query
        with open(query_file, 'r', encoding='utf-8') as f:
            query = f.read().strip()
        
        # Buscar archivo de variables (mismo nombre pero .variables.json)
        vars_file = query_file.parent / f"{query_file.stem}.variables.json"
        variables = {}
        
        if vars_file.exists():
            with open(vars_file, 'r', encoding='utf-8') as f:
                variables = json.load(f)
        
        return query, variables
        
    except Exception as e:
        print(f"Error al leer el query {query_file}: {e}")
        return None


def graphql_to_csv(results: List[Dict[str, Any]], output_file: Path, query_name: str):
    """
    Convierte las respuestas de GraphQL (múltiples páginas) a CSV.
    """
    try:
        all_rows_data = extract_rows_from_graphql_response(results)
        
        if not all_rows_data:
            print(f"  ⚠ No se encontraron datos para guardar en CSV para {query_name}")
            if results:
                print(f"  Estructura recibida: {list(results[0].keys())}")
                if 'data' in results[0]:
                    print(f"  Estructura de data: {list(results[0]['data'].keys())}")
            return
        
        # Aplanar cada fila
        flattened_rows = []
        for row in all_rows_data:
            flattened = flatten_dict(row)
            flattened_rows.append(flattened)
        
        if not flattened_rows:
            print(f"  ⚠ No hay filas para escribir para {query_name}")
            return
        
        # Escribir CSV
        write_csv(flattened_rows, output_file)
        print(f"  ✓ CSV guardado: {output_file} ({len(flattened_rows)} filas)")
        
    except Exception as e:
        print(f"  ✗ ERROR al convertir a CSV para {query_name}: {e}")
        import traceback
        traceback.print_exc()


def main():
    """
    Función principal: hace login y ejecuta todos los queries GraphQL desde archivos.
    """
    # Crear carpeta output/api si no existe
    results_dir = Path('output/api')
    results_dir.mkdir(parents=True, exist_ok=True)
    
    # Verificar que existe el directorio de queries
    if not GRAPHQL_DIR.exists():
        print(f"\n✗ ERROR: El directorio {GRAPHQL_DIR} no existe.")
        return
    
    # Buscar todos los archivos .graphql
    graphql_files = sorted(list(GRAPHQL_DIR.glob("*.graphql")))
    
    if not graphql_files:
        print(f"\n✗ ERROR: No se encontraron archivos .graphql en {GRAPHQL_DIR}")
        return
    
    # Hacer login
    token = login()
    if not token:
        print("\n✗ No se pudo obtener el token. Abortando.")
        return
    
    # Ejecutar cada query
    print("\n" + "="*70)
    print("Ejecutando queries GraphQL desde archivos...")
    print(f"Archivos encontrados: {len(graphql_files)}")
    print("="*70)
    
    for graphql_file in graphql_files:
        query_name = graphql_file.stem
        
        # Cargar query y variables
        query_data = load_graphql_query(graphql_file)
        
        if not query_data:
            print(f"\n✗ Error al cargar {graphql_file.name}, saltando...")
            continue
        
        query, variables = query_data
        
        # Ejecutar el query
        results = graphql_request(
            token=token,
            query=query,
            variables=variables,
            query_name=query_name,
            paginate=True
        )
        
        if results:
            output_file = results_dir / f"{query_name}.csv"
            graphql_to_csv(results, output_file, query_name)
    
    print("\n" + "="*70)
    print("✓ Proceso completado")
    print(f"Resultados guardados en: {results_dir.absolute()}")
    print("="*70)


if __name__ == "__main__":
    main()
