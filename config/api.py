"""Configuración de la API"""
import os

API_CONFIG = {
    'base_url': os.getenv('API_BASE_URL', 'https://apinewtm.com'),
    'graphql_endpoint': os.getenv('API_GRAPHQL_ENDPOINT', '/graphql/'),
    'auth_endpoint': os.getenv('API_AUTH_ENDPOINT', '/api/auth/token'),
    'tenant_name': os.getenv('API_TENANT_NAME', 'emba'),
    'username': os.getenv('API_USERNAME', 'hmarquez@emba.com.bo'),
    'password': os.getenv('API_PASSWORD', 'mv-4XdPtzHEu'),
    'origin': os.getenv('API_ORIGIN', 'https://azure-function.timemanagerweb.com')
}

