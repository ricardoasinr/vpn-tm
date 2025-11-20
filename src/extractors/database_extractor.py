#!/usr/bin/env python3
"""
Extractor de datos desde base de datos MySQL.
Ejecuta todos los queries SQL en queries/sql/ y guarda los resultados en CSV.
"""
import sys
import csv
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.database.connection import get_db_connection


def execute_queries_to_csv():
    """Ejecuta todos los queries SQL y los guarda como CSV"""
    try:
        import pymysql
        
        # Crear carpeta output/database si no existe
        results_dir = Path('output/database')
        results_dir.mkdir(parents=True, exist_ok=True)
        
        # Carpeta de queries SQL
        queries_dir = Path('queries/sql')
        
        if not queries_dir.exists():
            print(f"\n✗ ERROR: La carpeta 'queries/sql' no existe")
            return
        
        # Buscar todos los archivos .sql recursivamente
        sql_files = list(queries_dir.rglob('*.sql'))
        
        if not sql_files:
            print(f"\n✗ ERROR: No se encontraron archivos .sql en la carpeta 'queries/sql'")
            return
        
        print("\n" + "="*70)
        print("Ejecutando queries y guardando resultados en CSV...")
        print(f"Archivos encontrados: {len(sql_files)}")
        print("="*70)
        
        # Conectar a la base de datos
        try:
            conn = get_db_connection()
            print("✓ Conexión a la base de datos establecida\n")
        except Exception as e:
            print(f"\n✗ ERROR al conectar a la base de datos: {e}")
            return
        
        cursor = conn.cursor()
        
        # Procesar cada archivo SQL
        for sql_file in sql_files:
            try:
                print(f"Procesando: {sql_file.name}...")
                
                # Leer el contenido del archivo SQL
                with open(sql_file, 'r', encoding='utf-8') as f:
                    query = f.read()
                
                # Ejecutar el query
                cursor.execute(query)
                
                # Obtener los resultados
                results = cursor.fetchall()
                
                # Obtener los nombres de las columnas
                column_names = [desc[0] for desc in cursor.description]
                
                # Crear el nombre del archivo CSV (mismo nombre pero con extensión .csv)
                csv_filename = sql_file.stem + '.csv'
                csv_path = results_dir / csv_filename
                
                # Escribir a CSV
                with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    
                    # Escribir encabezados
                    writer.writerow(column_names)
                    
                    # Escribir datos
                    writer.writerows(results)
                
                print(f"  ✓ Guardado: {csv_path} ({len(results)} filas)")
                
            except pymysql.Error as e:
                print(f"  ✗ ERROR al ejecutar query {sql_file.name}: {e}")
            except Exception as e:
                print(f"  ✗ ERROR inesperado con {sql_file.name}: {e}")
                import traceback
                traceback.print_exc()
        
        cursor.close()
        conn.close()
        
        print("\n" + "="*70)
        print("✓ Proceso completado")
        print(f"Resultados guardados en: {results_dir.absolute()}")
        print("="*70)
        
    except ImportError:
        print("\n" + "="*70)
        print("✗ ERROR: pymysql no está instalado.")
        print("="*70)
        print("Instálalo con: pip install pymysql")
        print("="*70)
    except Exception as e:
        print(f"\n✗ ERROR inesperado: {type(e).__name__}: {e}")
        import traceback
        print("\nDetalles del error:")
        traceback.print_exc()


def main():
    """Función principal"""
    execute_queries_to_csv()


if __name__ == "__main__":
    main()

