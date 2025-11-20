#!/usr/bin/env python3
"""
Extractor interactivo de datos desde la API GraphQL.
Permite seleccionar qué query ejecutar desde un menú interactivo.
Lee queries GraphQL desde archivos .graphql y variables desde .variables.json
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


def list_graphql_queries():
    """Lista todos los archivos .graphql disponibles."""
    if not GRAPHQL_DIR.exists():
        print(f"Error: El directorio {GRAPHQL_DIR} no existe.")
        return []
    
    graphql_files = sorted([f for f in GRAPHQL_DIR.glob("*.graphql")])
    return graphql_files


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


def save_results(results: List[Dict[str, Any]], query_name: str):
    """
    Guarda las respuestas en JSON y CSV.
    """
    if not results:
        print(f"  ⚠ No hay resultados para guardar para {query_name}")
        return
    
    # Crear directorio de resultados si no existe
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Guardar JSON
    json_file = RESULTS_DIR / f"{query_name}.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"  ✓ JSON guardado: {json_file}")
    
    # Guardar CSV
    try:
        all_rows_data = extract_rows_from_graphql_response(results)
        
        if all_rows_data:
            # Aplanar cada fila
            flattened_rows = []
            for row in all_rows_data:
                flattened = flatten_dict(row)
                flattened_rows.append(flattened)
            
            # Escribir CSV
            csv_file = RESULTS_DIR / f"{query_name}.csv"
            write_csv(flattened_rows, csv_file)
            
            print(f"  ✓ CSV guardado: {csv_file} ({len(flattened_rows)} filas)")
        else:
            print(f"  ⚠ No se encontraron datos para guardar en CSV para {query_name}")
            
    except Exception as e:
        print(f"  ✗ ERROR al convertir a CSV para {query_name}: {e}")


def execute_graphql_query(query: str, variables: Dict[str, Any], query_name: str, token: str):
    """
    Ejecuta un query GraphQL, maneja paginación y guarda resultados.
    """
    if not query:
        print("✗ Error: Query vacío")
        return False
    
    # Ejecutar con paginación usando el cliente GraphQL
    results = graphql_request(
        token=token,
        query=query,
        variables=variables,
        query_name=query_name,
        paginate=True
    )
    
    if results:
        # Guardar resultados
        save_results(results, query_name)
        return True
    else:
        return False


def show_menu(token: str):
    """Muestra el menú interactivo y permite seleccionar un query GraphQL."""
    graphql_files = list_graphql_queries()
    
    if not graphql_files:
        print("No se encontraron archivos .graphql en el directorio.")
        return
    
    print("\n" + "="*80)
    print("MENÚ DE QUERIES GRAPHQL")
    print("="*80)
    print("\nQueries disponibles:\n")
    
    for idx, file_path in enumerate(graphql_files, 1):
        file_name = file_path.name
        print(f"  {idx}. {file_name}")
    
    print(f"  0. Salir")
    print("\n" + "="*80)
    
    while True:
        try:
            choice = input("\nSelecciona el número del query que deseas ejecutar: ").strip()
            
            if choice == "0":
                print("Saliendo...")
                return
            
            choice_num = int(choice)
            
            if 1 <= choice_num <= len(graphql_files):
                selected_file = graphql_files[choice_num - 1]
                file_name = selected_file.name
                
                print(f"\n{'='*80}")
                print(f"Ejecutando: {file_name}")
                print(f"{'='*80}\n")
                
                # Cargar query y variables
                query_data = load_graphql_query(selected_file)
                
                if query_data:
                    query, variables = query_data
                    # Obtener nombre del query (sin extensión)
                    query_name = file_name.replace('.graphql', '')
                    
                    # Ejecutar el query con paginación y guardar resultados
                    success = execute_graphql_query(query, variables, query_name, token)
                    
                    if success:
                        print(f"\n{'='*80}")
                        print(f"✓ Proceso completado para {query_name}")
                        print(f"Resultados guardados en: {RESULTS_DIR.absolute()}")
                        print(f"{'='*80}")
                    
                    # Preguntar si quiere ejecutar otro
                    print("\n")
                    again = input("¿Deseas ejecutar otro query? (s/n): ").strip().lower()
                    if again not in ['s', 'si', 'sí', 'y', 'yes']:
                        break
                    else:
                        # Mostrar el menú de nuevo
                        print("\n" + "="*80)
                        print("MENÚ DE QUERIES GRAPHQL")
                        print("="*80)
                        print("\nQueries disponibles:\n")
                        for idx, file_path in enumerate(graphql_files, 1):
                            print(f"  {idx}. {file_path.name}")
                        print(f"  0. Salir")
                        print("\n" + "="*80)
                else:
                    print(f"Error: No se pudo cargar el query {file_name}")
                    break
            else:
                print(f"Error: Por favor selecciona un número entre 1 y {len(graphql_files)}, o 0 para salir.")
        
        except ValueError:
            print("Error: Por favor ingresa un número válido.")
        except KeyboardInterrupt:
            print("\n\nOperación cancelada por el usuario.")
            break
        except Exception as e:
            print(f"Error inesperado: {e}")
            break


def main():
    """Función principal."""
    # Hacer login primero
    token = login()
    if not token:
        print("\n✗ No se pudo obtener el token. Abortando.")
        return
    
    show_menu(token)


if __name__ == "__main__":
    main()

