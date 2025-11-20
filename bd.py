import os
import sys
import csv
import glob
from pathlib import Path

# Configuración de la base de datos Aurora MySQL
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'tmdb-aurora-cluster.cluster-ro-cmt9q0z4t4rd.us-east-1.rds.amazonaws.com'),
    'port': int(os.getenv('DB_PORT', '3306')),  # Puerto de MySQL
    'database': os.getenv('DB_NAME', 'tm_emba'),
    'user': os.getenv('DB_USER', 'tm_emba_readonly'),
    'password': os.getenv('DB_PASSWORD', 'X(VB#G0FAfDth')
}


def get_db_connection():
    """Obtiene una conexión a la base de datos"""
    import pymysql
    return pymysql.connect(
        host=DB_CONFIG['host'],
        port=DB_CONFIG['port'],
        database=DB_CONFIG['database'],
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password'],
        connect_timeout=10,
        ssl={'ca': None}
    )


def list_database_tables():
    """Conecta a la base de datos MySQL y lista las tablas (sin VPN, conexión directa)"""
    try:
        # Para MySQL
        import pymysql
        
        print("\n" + "="*70)
        print("Conectando a la base de datos MySQL (conexión directa, sin VPN)...")
        print(f"Host: {DB_CONFIG['host']}")
        print(f"Port: {DB_CONFIG['port']}")
        print(f"Database: {DB_CONFIG['database']}")
        print(f"User: {DB_CONFIG['user']}")
        print("="*70)
        
        try:
            conn = get_db_connection()
            print("✓ Conexión a la base de datos establecida")
        except pymysql.Error as e:
            print(f"\n✗ ERROR al conectar a la base de datos:")
            print(f"  {e}")
            print("\nPosibles causas:")
            print("  1. El host de la base de datos no es accesible desde tu red")
            print("  2. Las credenciales son incorrectas")
            print("  3. El firewall bloquea la conexión")
            print("  4. La base de datos requiere VPN para acceder")
            return
        except Exception as e:
            print(f"\n✗ ERROR inesperado: {e}")
            return
        
        cursor = conn.cursor()
        
        # Query para listar tablas (MySQL/Aurora)
        # Lista todas las tablas de todos los esquemas accesibles
        print("\nConsultando tablas...")
        cursor.execute("""
            SELECT table_schema, table_name 
            FROM information_schema.tables 
            WHERE table_schema NOT IN ('information_schema', 'performance_schema', 'mysql', 'sys')
            ORDER BY table_schema, table_name;
        """)
        
        tables = cursor.fetchall()
        
        print("\n" + "="*70)
        print("TABLAS EN LA BASE DE DATOS:")
        print("="*70)
        
        if tables:
            current_schema = None
            for schema, table_name in tables:
                if schema != current_schema:
                    current_schema = schema
                    print(f"\n[{schema}]")
                print(f"  - {table_name}")
        else:
            print("  No se encontraron tablas")
        
        print("="*70)
        print(f"Total de tablas: {len(tables)}")
        
        cursor.close()
        conn.close()
        print("\n✓ Conexión a la base de datos cerrada")
        
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


def execute_queries_to_csv():
    """Ejecuta todos los queries en la carpeta queries y los guarda como CSV en results"""
    try:
        import pymysql
        
        # Crear carpeta results si no existe
        results_dir = Path('results')
        results_dir.mkdir(exist_ok=True)
        
        # Carpeta de queries
        queries_dir = Path('queries')
        
        if not queries_dir.exists():
            print(f"\n✗ ERROR: La carpeta 'queries' no existe")
            return
        
        # Buscar todos los archivos .sql
        sql_files = list(queries_dir.glob('*.sql'))
        
        if not sql_files:
            print(f"\n✗ ERROR: No se encontraron archivos .sql en la carpeta 'queries'")
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
    # Ejecutar queries y guardar en CSV
    execute_queries_to_csv()


if __name__ == "__main__":
    main()

