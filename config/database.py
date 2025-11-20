"""Configuración de la base de datos"""
import os

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'tmdb-aurora-cluster.cluster-ro-cmt9q0z4t4rd.us-east-1.rds.amazonaws.com'),
    'port': int(os.getenv('DB_PORT', '3306')),
    'database': os.getenv('DB_NAME', 'tm_emba'),
    'user': os.getenv('DB_USER', 'tm_emba_readonly'),
    'password': os.getenv('DB_PASSWORD', 'X(VB#G0FAfDth')
}

