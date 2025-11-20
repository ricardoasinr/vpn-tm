import subprocess
import time
import signal
import sys
import os

# Configuración de la base de datos Aurora MySQL
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'tmdb-aurora-cluster.cluster-ro-cmt9q0z4t4rd.us-east-1.rds.amazonaws.com'),
    'port': int(os.getenv('DB_PORT', '3306')),  # Puerto de MySQL
    'database': os.getenv('DB_NAME', 'tm_emba'),
    'user': os.getenv('DB_USER', 'tm_emba_readonly'),
    'password': os.getenv('DB_PASSWORD', 'X(VB#G0FAfDth')
}

config_path = "mb.ovpn"
vpn_process = None


def check_vpn_interface():
    """Verifica si la interfaz VPN (tun/tap) está activa"""
    try:
        # Verifica interfaces tun (tun0, tun1, etc.)
        result = subprocess.run(
            ["ifconfig"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if "tun" in result.stdout.lower():
            return True
        
        # También verifica con ip (si está disponible en macOS)
        result = subprocess.run(
            ["ip", "link", "show"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0 and "tun" in result.stdout.lower():
            return True
        
        return False
    except:
        return False


def find_openvpn_binary():
    """Busca el binario de OpenVPN en ubicaciones comunes"""
    possible_paths = [
        "/usr/local/bin/openvpn",
        "/opt/homebrew/bin/openvpn",
        "/usr/bin/openvpn",
        "/Applications/Tunnelblick.app/Contents/Resources/openvpn",
        "/Applications/Viscosity.app/Contents/Resources/openvpn",
    ]
    
    # También busca en el PATH
    try:
        result = subprocess.run(["which", "openvpn"], capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except:
        pass
    
    # Busca en rutas comunes
    for path in possible_paths:
        if os.path.exists(path) and os.access(path, os.X_OK):
            return path
    
    return None


def connect_vpn():
    """Conecta a la VPN de AWS Client VPN"""
    global vpn_process
    print("="*70)
    print("Verificando conexión VPN...")
    print(f"Endpoint: cvpn-endpoint-034bc5632a1cbc6c4.prod.clientvpn.us-east-1.amazonaws.com")
    print("="*70)
    
    # Primero verifica si la VPN ya está conectada
    print("Verificando si la VPN ya está conectada...")
    if check_vpn_interface():
        print("✓ VPN ya está conectada (interfaz detectada)")
        return True
    
    print("VPN no detectada. Intentando conectar...")
    
    # Verifica que el archivo de configuración exista
    if not os.path.exists(config_path):
        print(f"ERROR: No se encuentra el archivo de configuración: {config_path}")
        return False
    
    # Busca el binario de OpenVPN
    openvpn_binary = find_openvpn_binary()
    if not openvpn_binary:
        print("\n⚠ OpenVPN no se encontró como binario de línea de comandos.")
        print("Esto es normal si usas una aplicación GUI (Tunnelblick, Viscosity, etc.)")
        print("\nOpciones:")
        print("  1. Conéctate manualmente a la VPN usando tu aplicación")
        print("  2. O instala OpenVPN vía Homebrew: brew install openvpn")
        print("\nEsperando 10 segundos para que te conectes manualmente...")
        print("(Presiona Ctrl+C si ya estás conectado)")
        
        for i in range(10):
            time.sleep(1)
            if check_vpn_interface():
                print(f"\n✓ VPN detectada! Continuando...")
                return True
            print(".", end="", flush=True)
        
        print("\n⚠ No se detectó conexión VPN.")
        print("Si ya estás conectado, el script continuará de todas formas...")
        return True  # Continuamos de todas formas
    
    print(f"✓ OpenVPN encontrado en: {openvpn_binary}")
    
    # Ejecuta OpenVPN en background
    try:
        vpn_process = subprocess.Popen(
            ["sudo", openvpn_binary, "--config", config_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,  # Combina stderr con stdout
            text=True,
            bufsize=1  # Line buffered
        )
    except FileNotFoundError:
        print("ERROR: No se pudo ejecutar OpenVPN")
        return False
    except Exception as e:
        print(f"ERROR al ejecutar OpenVPN: {e}")
        return False
    
    # Espera a que la VPN se conecte (lee mensajes de OpenVPN)
    print("Esperando conexión VPN (esto puede tomar 15-30 segundos)...")
    print("Leyendo mensajes de OpenVPN...")
    
    vpn_connected = False
    max_wait = 30  # Máximo 30 segundos
    start_time = time.time()
    
    # Lee la salida de OpenVPN línea por línea
    output_lines = []
    while time.time() - start_time < max_wait:
        if vpn_process.poll() is not None:
            # El proceso terminó, algo salió mal
            # Lee toda la salida restante
            remaining_output = vpn_process.stdout.read() if vpn_process.stdout else ""
            all_output = '\n'.join(output_lines) + '\n' + remaining_output
            print(f"\n✗ ERROR: El proceso de VPN terminó inesperadamente")
            print("Últimos mensajes de OpenVPN:")
            if all_output:
                # Muestra las últimas líneas
                lines = all_output.strip().split('\n')
                for line in lines[-15:]:  # Muestra más líneas para debug
                    if line.strip():
                        print(f"  {line}")
            else:
                print("  (No hay salida disponible)")
            return False
        
        # Verifica si hay salida disponible
        line = vpn_process.stdout.readline()
        if line:
            line = line.strip()
            output_lines.append(line)
            # Muestra mensajes importantes en tiempo real
            if "error" in line.lower() or "failed" in line.lower() or "fatal" in line.lower():
                print(f"\n⚠ {line}")
            elif "warning" in line.lower():
                print(f"\n⚠ {line}")
            # Busca el mensaje de conexión exitosa
            if "initialization sequence completed" in line.lower():
                print(f"\n✓ OpenVPN reporta: {line}")
                vpn_connected = True
                break
        
        time.sleep(0.5)
        print(".", end="", flush=True)
    
    if not vpn_connected:
        print("\n⚠ No se detectó el mensaje de conexión completa de OpenVPN")
        print("Verificando interfaz de red...")
    
    # Espera un poco más y verifica la interfaz de red
    print("\nEsperando estabilización de la conexión...")
    for i in range(5):
        time.sleep(1)
        if check_vpn_interface():
            print(f"✓ Interfaz VPN detectada (intento {i+1}/5)")
            vpn_connected = True
            break
        print(".", end="", flush=True)
    
    if not vpn_connected:
        print("\n⚠ ADVERTENCIA: No se pudo verificar completamente la conexión VPN")
        print("Continuando de todas formas...")
        print("Si falla la conexión a la BD, verifica manualmente la VPN")
    else:
        print("\n✓ VPN conectada y verificada exitosamente")
    
    return True


def list_database_tables():
    """Conecta a la base de datos MySQL y lista las tablas"""
    try:
        # Para MySQL
        import pymysql
        
        print("\n" + "="*70)
        print("Conectando a la base de datos MySQL...")
        print(f"Host: {DB_CONFIG['host']}")
        print(f"Port: {DB_CONFIG['port']}")
        print(f"Database: {DB_CONFIG['database']}")
        print(f"User: {DB_CONFIG['user']}")
        print("="*70)
        
        try:
            # Configuración SSL para AWS RDS/Aurora MySQL
            # pymysql usa SSL por defecto si el servidor lo requiere
            conn = pymysql.connect(
                host=DB_CONFIG['host'],
                port=DB_CONFIG['port'],
                database=DB_CONFIG['database'],
                user=DB_CONFIG['user'],
                password=DB_CONFIG['password'],
                connect_timeout=10,
                ssl={'ca': None}  # Usa certificados del sistema
            )
            print("✓ Conexión a la base de datos establecida")
        except pymysql.Error as e:
            print(f"\n✗ ERROR al conectar a la base de datos:")
            print(f"  {e}")
            print("\nPosibles causas:")
            print("  1. La VPN no está completamente conectada")
            print("  2. El host de la base de datos no es accesible desde la VPN")
            print("  3. Las credenciales son incorrectas")
            print("  4. El firewall bloquea la conexión")
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


def cleanup():
    """Cierra la conexión VPN al terminar"""
    global vpn_process
    if vpn_process:
        print("\nCerrando conexión VPN...")
        vpn_process.terminate()
        vpn_process.wait()
        print("VPN desconectada")


def signal_handler(sig, frame):
    """Maneja señales de interrupción (Ctrl+C)"""
    cleanup()
    sys.exit(0)


def main():
    """Función principal"""
    # Configura el manejador de señales para limpiar al salir
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Conecta a la VPN
        if not connect_vpn():
            print("No se pudo conectar a la VPN. Saliendo...")
            return
        
        # Espera un poco más para asegurar que la conexión esté estable
        print("\nEsperando 10 segundos adicionales para que la VPN se estabilice completamente...")
        for i in range(10):
            time.sleep(1)
            print(".", end="", flush=True)
        print()
        
        # Test de conectividad básico
        print("\nRealizando test de conectividad...")
        try:
            # Intenta hacer ping o verificar conectividad de red
            result = subprocess.run(
                ["ping", "-c", "1", "-W", "2000", DB_CONFIG['host']],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                print("✓ El host de la base de datos es alcanzable")
            else:
                print("⚠ No se pudo hacer ping al host (puede ser normal si el firewall bloquea ICMP)")
        except Exception as e:
            print(f"⚠ No se pudo verificar conectividad: {e}")
        
        # Conecta a la base de datos y lista las tablas
        list_database_tables()
        
        # Mantiene el script corriendo (opcional, comenta si quieres que termine)
        print("\nPresiona Ctrl+C para desconectar y salir...")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        cleanup()


if __name__ == "__main__":
    main()
