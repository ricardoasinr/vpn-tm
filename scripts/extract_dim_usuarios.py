#!/usr/bin/env python3
"""
Script para ejecutar el extractor de Dim_Usuarios desde la API GraphQL.
"""
import sys
import json
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.api.auth import login
from src.api.client import graphql_request
from src.utils.graphql_parser import extract_rows_from_graphql_response
from src.utils.json_flattener import flatten_dict
from src.utils.csv_writer import write_csv

# Configuración
QUERY_NAME = "dim_usuarios"
GRAPHQL_DIR = Path('queries/graphql')
RESULTS_DIR = Path('output/api')


def main():
    """Ejecuta el extractor de Dim_Usuarios"""
    print("="*80)
    print("EXTRACTOR: Dim_Usuarios (API GraphQL)")
    print("="*80)
    
    # Crear carpeta output/api si no existe
    results_dir = RESULTS_DIR
    results_dir.mkdir(parents=True, exist_ok=True)
    
    # Archivos del query
    query_file = GRAPHQL_DIR / f"{QUERY_NAME}.graphql"
    vars_file = GRAPHQL_DIR / f"{QUERY_NAME}.variables.json"
    
    # Verificar que existen los archivos
    if not query_file.exists():
        print(f"\n✗ ERROR: El archivo {query_file} no existe.")
        return
    
    # Leer el query
    try:
        with open(query_file, 'r', encoding='utf-8') as f:
            query = f.read().strip()
    except Exception as e:
        print(f"\n✗ ERROR al leer el query: {e}")
        return
    
    # Leer variables si existe el archivo
    variables = {}
    if vars_file.exists():
        try:
            with open(vars_file, 'r', encoding='utf-8') as f:
                variables = json.load(f)
        except Exception as e:
            print(f"⚠ Advertencia: No se pudieron cargar las variables: {e}")
    
    # Hacer login
    print("\n🔐 Autenticando...")
    token = login()
    if not token:
        print("\n✗ No se pudo obtener el token. Abortando.")
        return
    print("✓ Autenticación exitosa")
    
    # Ejecutar el query
    print(f"\n📊 Ejecutando query: {QUERY_NAME}")
    print("-"*80)
    
    results = graphql_request(
        token=token,
        query=query,
        variables=variables,
        query_name=QUERY_NAME,
        paginate=True
    )
    
    if not results:
        print(f"\n✗ No se obtuvieron resultados para {QUERY_NAME}")
        return
    
    # Convertir a CSV
    print(f"\n💾 Guardando resultados...")
    try:
        all_rows_data = extract_rows_from_graphql_response(results)
        
        if not all_rows_data:
            print(f"  ⚠ No se encontraron datos para guardar en CSV")
            return
        
        # Aplanar cada fila
        flattened_rows = []
        for row in all_rows_data:
            flattened = flatten_dict(row)
            flattened_rows.append(flattened)
        
        if not flattened_rows:
            print(f"  ⚠ No hay filas para escribir")
            return
        
        # Escribir CSV
        output_file = results_dir / f"{QUERY_NAME}.csv"
        write_csv(flattened_rows, output_file)
        print(f"  ✓ CSV guardado: {output_file} ({len(flattened_rows)} filas)")
        
    except Exception as e:
        print(f"  ✗ ERROR al convertir a CSV: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print("\n" + "="*80)
    print("✓ EXTRACCIÓN COMPLETADA")
    print(f"Resultado guardado en: {output_file.absolute()}")
    print("="*80)


if __name__ == "__main__":
    main()

