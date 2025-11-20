#!/usr/bin/env python3
"""
Script interactivo para ejecutar comandos curl desde archivos.
Permite seleccionar qué curl ejecutar desde un menú.
Maneja paginación automáticamente y guarda las respuestas en JSON y CSV.
"""

import os
import json
import csv
import re
import requests
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

# Directorio donde están los archivos curl
CURLS_DIR = Path(__file__).parent / "curls"
RESULTS_DIR = Path(__file__).parent / "results_curl"


def list_curl_files():
    """Lista todos los archivos .txt en el directorio curls."""
    if not CURLS_DIR.exists():
        print(f"Error: El directorio {CURLS_DIR} no existe.")
        return []
    
    curl_files = sorted([f for f in CURLS_DIR.glob("*.txt")])
    return curl_files


def read_curl_file(file_path):
    """Lee el contenido de un archivo curl."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except Exception as e:
        print(f"Error al leer el archivo {file_path}: {e}")
        return None


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
        # Reemplazar \n con newlines reales
        data_str = data_str.replace('\\n', '\n')
        data_dict = json.loads(data_str)
        
        return url, headers, data_dict
        
    except Exception as e:
        print(f"Error al parsear comando curl: {e}")
        return None


def execute_graphql_with_pagination(url: str, headers: Dict[str, str], query: str, 
                                     variables: Dict[str, Any], query_name: str) -> Optional[List[Dict[str, Any]]]:
    """
    Ejecuta un query GraphQL con paginación automática.
    
    Returns:
        Lista de todas las respuestas de todas las páginas o None si hay error
    """
    print(f"\nEjecutando query: {query_name}...")
    
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
            data_obj = result.get('data', {})
            has_next = False
            
            # Para BusinessMeta
            if 'BusinessMeta' in data_obj:
                meta = data_obj['BusinessMeta'].get('meta', {})
                has_next = meta.get('hasNextPage', False)
                total = meta.get('total', 0)
                current_total = len(data_obj['BusinessMeta'].get('rows', []))
                print(f"  Página {current_page}: {current_total} registros (Total: {total})")
            
            # Para Users
            elif 'Users' in data_obj:
                meta = data_obj['Users'].get('meta', {})
                has_next = meta.get('hasNextPage', False)
                total = meta.get('total', 0)
                current_total = len(data_obj['Users'].get('users', []))
                print(f"  Página {current_page}: {current_total} registros (Total: {total})")
            
            # Para TimesByFiltersPaged
            elif 'TimesByFiltersPaged' in data_obj:
                times_data = data_obj['TimesByFiltersPaged']
                has_next = times_data.get('has_next_page', False)
                total = times_data.get('total', 0)
                current_total = len(times_data.get('times', []))
                print(f"  Página {current_page}: {current_total} registros (Total: {total})")
            
            else:
                # No hay paginación o estructura desconocida
                print(f"  Respuesta recibida (sin paginación detectada)")
                break
            
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


def flatten_dict(d: Dict[str, Any], parent_key: str = '', sep: str = '_') -> Dict[str, Any]:
    """Aplana un diccionario anidado."""
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        elif isinstance(v, list):
            items.append((new_key, json.dumps(v) if v else ''))
        else:
            items.append((new_key, v))
    return dict(items)


def save_results(results: List[Dict[str, Any]], query_name: str):
    """
    Guarda las respuestas en JSON y CSV.
    """
    if not results:
        print(f"  ⚠ No hay resultados para guardar para {query_name}")
        return
    
    # Crear directorio de resultados si no existe
    RESULTS_DIR.mkdir(exist_ok=True)
    
    # Guardar JSON
    json_file = RESULTS_DIR / f"{query_name}.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"  ✓ JSON guardado: {json_file}")
    
    # Guardar CSV
    try:
        all_rows_data = []
        
        # Procesar cada página de resultados
        for data in results:
            rows_data = None
            
            if 'data' in data:
                data_obj = data['data']
                
                # Para BusinessMeta
                if 'BusinessMeta' in data_obj:
                    business_meta = data_obj['BusinessMeta']
                    if 'rows' in business_meta:
                        rows_data = business_meta['rows']
                
                # Para Users
                elif 'Users' in data_obj:
                    users = data_obj['Users']
                    if 'users' in users:
                        rows_data = users['users']
                
                # Para TimesByFiltersPaged
                elif 'TimesByFiltersPaged' in data_obj:
                    times_data = data_obj['TimesByFiltersPaged']
                    if 'times' in times_data:
                        rows_data = times_data['times']
            
            if rows_data:
                all_rows_data.extend(rows_data)
        
        if all_rows_data:
            # Aplanar cada fila
            flattened_rows = []
            for row in all_rows_data:
                flattened = flatten_dict(row)
                flattened_rows.append(flattened)
            
            # Obtener todas las columnas posibles
            all_columns = set()
            for row in flattened_rows:
                all_columns.update(row.keys())
            
            columns = sorted(list(all_columns))
            
            # Escribir CSV
            csv_file = RESULTS_DIR / f"{query_name}.csv"
            with open(csv_file, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=columns, extrasaction='ignore')
                writer.writeheader()
                writer.writerows(flattened_rows)
            
            print(f"  ✓ CSV guardado: {csv_file} ({len(flattened_rows)} filas, {len(columns)} columnas)")
        else:
            print(f"  ⚠ No se encontraron datos para guardar en CSV para {query_name}")
            
    except Exception as e:
        print(f"  ✗ ERROR al convertir a CSV para {query_name}: {e}")


def execute_curl(curl_command: str, query_name: str):
    """
    Ejecuta un comando curl parseado, maneja paginación y guarda resultados.
    """
    # Parsear el comando curl
    parsed = parse_curl_command(curl_command)
    if not parsed:
        print("✗ Error: No se pudo parsear el comando curl")
        return False
    
    url, headers, data_dict = parsed
    
    # Extraer query y variables
    query = data_dict.get('query', '')
    variables = data_dict.get('variables', {})
    
    if not query:
        print("✗ Error: No se encontró query GraphQL en el comando curl")
        return False
    
    # Ejecutar con paginación
    results = execute_graphql_with_pagination(url, headers, query, variables, query_name)
    
    if results:
        # Guardar resultados
        save_results(results, query_name)
        return True
    else:
        return False


def show_menu():
    """Muestra el menú interactivo y permite seleccionar un curl."""
    curl_files = list_curl_files()
    
    if not curl_files:
        print("No se encontraron archivos curl en el directorio.")
        return
    
    print("\n" + "="*80)
    print("MENÚ DE COMANDOS CURL")
    print("="*80)
    print("\nArchivos disponibles:\n")
    
    for idx, file_path in enumerate(curl_files, 1):
        file_name = file_path.name
        print(f"  {idx}. {file_name}")
    
    print(f"  0. Salir")
    print("\n" + "="*80)
    
    while True:
        try:
            choice = input("\nSelecciona el número del curl que deseas ejecutar: ").strip()
            
            if choice == "0":
                print("Saliendo...")
                return
            
            choice_num = int(choice)
            
            if 1 <= choice_num <= len(curl_files):
                selected_file = curl_files[choice_num - 1]
                file_name = selected_file.name
                
                print(f"\n{'='*80}")
                print(f"Ejecutando: {file_name}")
                print(f"{'='*80}\n")
                
                # Leer el contenido del archivo
                curl_command = read_curl_file(selected_file)
                
                if curl_command:
                    # Obtener nombre del query (sin extensión)
                    query_name = file_name.replace('.txt', '')
                    
                    # Ejecutar el curl con paginación y guardar resultados
                    success = execute_curl(curl_command, query_name)
                    
                    if success:
                        print(f"\n{'='*80}")
                        print(f"✓ Proceso completado para {query_name}")
                        print(f"Resultados guardados en: {RESULTS_DIR.absolute()}")
                        print(f"{'='*80}")
                    
                    # Preguntar si quiere ejecutar otro
                    print("\n")
                    again = input("¿Deseas ejecutar otro curl? (s/n): ").strip().lower()
                    if again not in ['s', 'si', 'sí', 'y', 'yes']:
                        break
                    else:
                        # Mostrar el menú de nuevo
                        print("\n" + "="*80)
                        print("MENÚ DE COMANDOS CURL")
                        print("="*80)
                        print("\nArchivos disponibles:\n")
                        for idx, file_path in enumerate(curl_files, 1):
                            print(f"  {idx}. {file_path.name}")
                        print(f"  0. Salir")
                        print("\n" + "="*80)
                else:
                    print(f"Error: No se pudo leer el archivo {file_name}")
                    break
            else:
                print(f"Error: Por favor selecciona un número entre 1 y {len(curl_files)}, o 0 para salir.")
        
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
    show_menu()


if __name__ == "__main__":
    main()

