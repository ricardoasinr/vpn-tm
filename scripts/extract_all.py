#!/usr/bin/env python3
"""
Script para ejecutar todos los extractores en secuencia.
"""
import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.extractors.database_extractor import main as extract_database
from src.extractors.api_extractor import main as extract_api


def main():
    """Ejecuta todos los extractores"""
    print("="*80)
    print("EJECUTANDO TODOS LOS EXTRACTORES")
    print("="*80)
    
    print("\n1. Extrayendo desde base de datos...")
    print("-"*80)
    extract_database()
    
    print("\n\n2. Extrayendo desde API...")
    print("-"*80)
    extract_api()
    
    print("\n" + "="*80)
    print("✓ TODOS LOS EXTRACTORES COMPLETADOS")
    print("="*80)


if __name__ == "__main__":
    main()

