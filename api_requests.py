#!/usr/bin/env python3
"""
Script para hacer login y ejecutar requests POST usando el token de autenticación.
Las respuestas se guardan en archivos CSV.
"""

import json
import csv
import requests
from pathlib import Path
from typing import Dict, Any, List, Optional


def login() -> Optional[str]:
    """
    Hace login y retorna el bearer token.
    """
    print("="*70)
    print("Haciendo login...")
    print("="*70)
    
    url = "https://apinewtm.com/api/auth/token"
    
    headers = {
        'tenant-name': 'emba',
        'Origin': 'https://azure-function.timemanagerweb.com',
        'Content-Type': 'application/json'
    }
    
    data = {
        "username": "hmarquez@emba.com.bo",
        "password": "mv-4XdPtzHEu"
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
            # Si el token no está en los campos comunes, intentar buscar en la respuesta completa
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


def graphql_request(token: str, query: str, variables: Dict[str, Any], query_name: str, paginate: bool = True) -> Optional[List[Dict[str, Any]]]:
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
    
    url = "https://apinewtm.com/graphql/"
    
    headers = {
        'tenant-name': 'emba',
        'Origin': 'https://azure-function.timemanagerweb.com',
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
            
            # Obtener información de paginación según el tipo de query
            data_obj = result.get('data', {})
            has_next = False
            
            # Para BusinessMeta y Users
            if 'BusinessMeta' in data_obj:
                meta = data_obj['BusinessMeta'].get('meta', {})
                has_next = meta.get('hasNextPage', False)
                total = meta.get('total', 0)
                limit = meta.get('limit', 100)
                current_total = len(data_obj['BusinessMeta'].get('rows', []))
                print(f"  Página {current_page}: {current_total} registros (Total: {total})")
            
            elif 'Users' in data_obj:
                meta = data_obj['Users'].get('meta', {})
                has_next = meta.get('hasNextPage', False)
                total = meta.get('total', 0)
                limit = meta.get('limit', 100)
                current_total = len(data_obj['Users'].get('users', []))
                print(f"  Página {current_page}: {current_total} registros (Total: {total})")
            
            # Para TimesByFiltersPaged
            elif 'TimesByFiltersPaged' in data_obj:
                times_data = data_obj['TimesByFiltersPaged']
                has_next = times_data.get('has_next_page', False)
                total = times_data.get('total', 0)
                current_total = len(times_data.get('times', []))
                max_per_page = current_variables.get('max_per_page', 100)
                print(f"  Página {current_page}: {current_total} registros (Total: {total})")
            
            else:
                # No hay paginación o estructura desconocida
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
    """
    Aplana un diccionario anidado.
    """
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        elif isinstance(v, list):
            # Si es una lista de objetos, no podemos aplanarla fácilmente
            # En su lugar, guardamos como JSON string
            items.append((new_key, json.dumps(v) if v else ''))
        else:
            items.append((new_key, v))
    return dict(items)


def graphql_to_csv(results: List[Dict[str, Any]], output_file: Path, query_name: str):
    """
    Convierte las respuestas de GraphQL (múltiples páginas) a CSV.
    
    Args:
        results: Lista de respuestas JSON de GraphQL (una por página)
        output_file: Archivo donde guardar el CSV
        query_name: Nombre del query (para identificar la estructura)
    """
    try:
        all_rows_data = []
        
        # Procesar cada página de resultados
        for data in results:
            rows_data = None
            
            # Intentar diferentes estructuras comunes de GraphQL
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
        
        # Obtener todas las columnas posibles (unión de todas las claves)
        all_columns = set()
        for row in flattened_rows:
            all_columns.update(row.keys())
        
        columns = sorted(list(all_columns))
        
        # Escribir CSV
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=columns, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(flattened_rows)
        
        print(f"  ✓ CSV guardado: {output_file} ({len(flattened_rows)} filas, {len(columns)} columnas)")
        
    except Exception as e:
        print(f"  ✗ ERROR al convertir a CSV para {query_name}: {e}")
        import traceback
        traceback.print_exc()


def main():
    """
    Función principal: hace login y ejecuta todos los queries.
    """
    # Crear carpeta results_api si no existe
    results_dir = Path('results_api')
    results_dir.mkdir(exist_ok=True)
    
    # Hacer login
    token = login()
    if not token:
        print("\n✗ No se pudo obtener el token. Abortando.")
        return
    
    # Definir los queries GraphQL
    queries = {
        'Dim_Asuntos': {
            'query': """query BusinessMeta($page: Int, $limit: Int, $searchTerm: String, $customers: [Int], $enabled: [Int], $orderBy: String, $orderDesc: Boolean, $enterpriseGroup: [Int], $practiceAreas: [Int], $billingModes: [Int], $billingGroups: [Int], $contactCounterParty: [Int], $status: [String], $billable: Boolean, $skipNoMilestoneBusiness: Boolean, $startCreationAt: DateTime, $endCreationAt: DateTime, $bpmStatus: [String], $expiration: String, $board: Int, $assigned: Boolean, $assignedUser: [Int], $assignedRole: [Int], $currency: Int, $billableItemStatus: [String], $hasTimes: Boolean, $dateFrom: DateTime, $dateTo: DateTime) {
  BusinessMeta(page: $page, limit: $limit, searchTerm: $searchTerm, customers: $customers, enabled: $enabled, orderBy: $orderBy, orderDesc: $orderDesc, enterpriseGroup: $enterpriseGroup, practiceAreas: $practiceAreas, billingModes: $billingModes, billingGroups: $billingGroups, contactCounterParty: $contactCounterParty, status: $status, billable: $billable, skipNoMilestoneBusiness: $skipNoMilestoneBusiness, startCreationAt: $startCreationAt, endCreationAt: $endCreationAt, bpmStatus: $bpmStatus, expiration: $expiration, board: $board, assigned: $assigned, assignedUser: $assignedUser, assignedRole: $assignedRole, currency: $currency, billableItemStatus: $billableItemStatus, hasTimes: $hasTimes, dateFrom: $dateFrom, dateTo: $dateTo) {
    meta {
      total
      page
      pages
      limit
      hasPreviousPage
      hasNextPage
      previous
      next
    }
    rows {
      id
      displayName
      isBillable
      businessDescription {
        id
        description
      }
      customer {
        id
        name
        trade_name
        displayName
        customer_classification {
          id
          name
        }
      }
      practiceArea {
        id
        name
      }
      billingMode {
        id
        description
      }
      milestones {
        id
        name
      }
      secondaryExternalCode
      hourLimit
      limitAlert
      currency {
        id
        shortName
      }
      billingCurrency {
        id
        shortName
      }
      status
      statusMarking
      bpmStatus {
        id
        label
      }
      bpmResponsible {
        id
        fullName
      }
      finishedDate
      estimatedFinishDate
      riskStatus
      created_at
      fix_rate_value
      expedient
      primary_external_code
      monthlyFixRateGroup {
        id
        name
        hour_limit
        rate
      }
      notes
      milestonesTotal
    }
  }
}""",
            'variables': {
                "enabled": [1, 0],
                "page": 1,
                "limit": 100,
                "orderBy": "",
                "orderDesc": False
            }
        },
        'Dim_Usuario': {
            'query': """query Users($limit: Int, $page: Int, $searchTerm: String, $userTypes: [Int], $practiceAreas: [Int], $hideSuperAdmin: Boolean, $start_date: DateTime, $end_date: DateTime, $created: Boolean, $roles: [Int], $category: Int, $showDisabled: Boolean, $order_by: String, $order_dir: Boolean, $onlyDisabled: Boolean) {
  Users(limit: $limit, page: $page, searchTerm: $searchTerm, userTypes: $userTypes, practiceAreas: $practiceAreas, hideSuperAdmin: $hideSuperAdmin, start_date: $start_date, end_date: $end_date, created: $created, roles: $roles, category: $category, showDisabled: $showDisabled, order_by: $order_by, order_dir: $order_dir, onlyDisabled: $onlyDisabled) {
    meta {
      total
      page
      pages
      limit
      hasPreviousPage
      hasNextPage
      previous
      next
    }
    users {
      id
      username
      fullName
      shortName
      userType
      email
      userCategory {
        name
      }
      daysAllow
      enabled
    }
  }
}""",
            'variables': {
                "page": 1,
                "limit": 100,
                "order_by": None,
                "order_dir": False
            }
        },
        'Hechos_Tiempos': {
            'query': """query TimesByFiltersPaged($users: [Int], $customers: [Int], $businesses: [Int], $status: [String], $billiable: Boolean, $date_from: DateTime, $date_to: DateTime, $order_by: String, $order_dir: Boolean, $page: Int, $max_per_page: Int, $access: IndicatorAccess, $contacts: [Int]) {
  TimesByFiltersPaged(users: $users, customers: $customers, businesses: $businesses, status: $status, billiable: $billiable, date_from: $date_from, date_to: $date_to, order_by: $order_by, order_dir: $order_dir, page: $page, max_per_page: $max_per_page, access: $access, contacts: $contacts) {
    total
    num_pages
    has_previous_page
    has_next_page
    current_page
    previous_page
    next_page
    times {
      id
      date
      user {
        id
        shortName
        fullName
      }
      business {
        id
        displayName
        currency {
          id
          shortName
        }
        businessDescription {
          description
        }
        customer {
          id
          name
          trade_name
          color
          displayName
        }
        procedureRate {
          id
          name
          year
          status
        }
      }
      procedureTransaction {
        id
        status
        procedure_rate_detail {
          id
          procedureRate {
            id
            name
            year
            status
          }
          name
          description
          rate
          currency {
            id
            shortName
            exchangeRate
            status
          }
          procedureExpenses
          expensesCurrency {
            id
          }
          procedureExpensesBilling
          expensesBillingCurrency {
            id
            shortName
            exchangeRate
            status
          }
        }
      }
      minutes
      startTime
      endTime
      billableMinutes
      detail
      office_id
      status {
        id
        name
      }
      statusMarking
      workflow_status {
        id
        name
      }
      task {
        id
      }
      activity {
        id
        spanishDescription
      }
      practice_area {
        id
        name
      }
      billable
      milestone {
        id
        name
      }
      shared
      customer_classification {
        id
        name
      }
    }
  }
}""",
            'variables': {
                "access": "ALL",
                "customers": [],
                "businesses": [],
                "contacts": [],
                "status": None,
                "billiable": None,
                "date_from": None,
                "date_to": None,
                "max_per_page": 100,
                "page": 1,
                "order_by": "date",
                "order_dir": True,
                "users": []
            }
        }
    }
    
    # Ejecutar cada query
    print("\n" + "="*70)
    print("Ejecutando queries GraphQL...")
    print("="*70)
    
    for query_name, query_info in queries.items():
        results = graphql_request(
            token=token,
            query=query_info['query'],
            variables=query_info['variables'],
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
