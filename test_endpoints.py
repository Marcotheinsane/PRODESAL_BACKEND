# Script para probar los endpoints de la API
# Uso: python test_endpoints.py

import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def main():
    print("=" * 60)
    print("TESTING INDAP API ENDPOINTS")
    print("=" * 60)
    
    # 1. Obtener token
    print("\n1. Obteniendo token...")
    token_response = requests.post(f"{BASE_URL}/token/", json={
        "username": "admin",
        "password": "admin"
    })
    
    if token_response.status_code == 200:
        token_data = token_response.json()
        access_token = token_data['access']
        print(f"✅ Token obtenido: {access_token[:50]}...")
    else:
        print(f"❌ Error: {token_response.text}")
        return
    
    # Headers con token
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    # 2. Listar clientes
    print("\n2. Listando clientes...")
    list_response = requests.get(f"{BASE_URL}/clientes/", headers=headers)
    if list_response.status_code == 200:
        data = list_response.json()
        print(f"✅ Total de clientes: {data.get('count', 0)}")
    else:
        print(f"❌ Error: {list_response.text}")
    
    # 3. Crear cliente
    print("\n3. Creando nuevo cliente...")
    new_client = {
        "rut": "16.000.000-0",
        "nombres": "CARLOS",
        "apellidos": "LOPEZ RIVERA",
        "sector": "PRUEBA",
        "es_beneficiario": True
    }
    create_response = requests.post(f"{BASE_URL}/clientes/", 
                                   json=new_client, 
                                   headers=headers)
    if create_response.status_code == 201:
        print(f"✅ Cliente creado: {create_response.json()['rut']}")
    else:
        print(f"❌ Error: {create_response.text}")
    
    # 4. Endpoint especial: beneficiarios
    print("\n4. Obteniendo beneficiarios...")
    beneficiarios_response = requests.get(f"{BASE_URL}/clientes/beneficiarios/", 
                                         headers=headers)
    if beneficiarios_response.status_code == 200:
        print(f"✅ Total de beneficiarios: {len(beneficiarios_response.json())}")
    else:
        print(f"❌ Error: {beneficiarios_response.text}")
    
    # 5. Endpoint especial: estadísticas por sector
    print("\n5. Obteniendo estadísticas por sector...")
    sector_response = requests.get(f"{BASE_URL}/clientes/por_sector/", 
                                  headers=headers)
    if sector_response.status_code == 200:
        data = sector_response.json()
        print("✅ Estadísticas por sector:")
        for sector in data:
            print(f"   {sector['sector']}: {sector['total']} clientes ({sector['beneficiarios']} beneficiarios)")
    else:
        print(f"❌ Error: {sector_response.text}")
    
    print("\n" + "=" * 60)
    print("PRUEBAS COMPLETADAS")
    print("=" * 60)

if __name__ == "__main__":
    main()
