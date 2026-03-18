from django.test import TestCase, Client
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from app.models import Clientes


class ClientesAPITestCase(TestCase):
    """Tests para los endpoints de Clientes API"""
    
    def setUp(self):
        """Preparar datos para las pruebas"""
        self.client = APIClient()
        
        # Crear usuario de prueba
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        # Crear cliente de prueba
        self.cliente = Clientes.objects.create(
            rut='14.428.024-5',
            nombres='MARITZA',
            apellidos='ABARCAS CORONADO',
            sector='QUITAQUI',
            es_beneficiario=False
        )
    
    def test_obtener_token(self):
        """Prueba obtener token JWT"""
        response = self.client.post('/api/v1/token/', {
            'username': 'testuser',
            'password': 'testpass123'
        }, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
    
    def test_listar_clientes_sin_autenticacion(self):
        """Prueba que listar clientes sin token retorna 401"""
        response = self.client.get('/api/v1/clientes/')
        self.assertEqual(response.status_code, 401)
    
    def test_listar_clientes_con_autenticacion(self):
        """Prueba listar clientes con autenticación"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/v1/clientes/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('results', response.data)
    
    def test_crear_cliente(self):
        """Prueba crear un nuevo cliente"""
        self.client.force_authenticate(user=self.user)
        data = {
            'rut': '15.000.000-0',
            'nombres': 'JUAN',
            'apellidos': 'PEREZ GONZALEZ',
            'sector': 'OTRO',
            'es_beneficiario': True
        }
        response = self.client.post('/api/v1/clientes/', data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Clientes.objects.count(), 2)
    
    def test_crear_cliente_rut_duplicado(self):
        """Prueba que no se puede crear cliente con RUT duplicado"""
        self.client.force_authenticate(user=self.user)
        data = {
            'rut': '14.428.024-5',  # RUT ya existe
            'nombres': 'OTRO',
            'apellidos': 'CLIENTE',
            'sector': 'OTRO'
        }
        response = self.client.post('/api/v1/clientes/', data, format='json')
        self.assertEqual(response.status_code, 400)
    
    def test_validar_rut_formato(self):
        """Prueba validación de formato RUT"""
        self.client.force_authenticate(user=self.user)
        data = {
            'rut': 'INVALIDO',  # Formato inválido
            'nombres': 'TEST',
            'apellidos': 'USER',
            'sector': 'TEST'
        }
        response = self.client.post('/api/v1/clientes/', data, format='json')
        self.assertEqual(response.status_code, 400)
    
    def test_endpoint_beneficiarios(self):
        """Prueba endpoint especial de beneficiarios"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/v1/clientes/beneficiarios/')
        self.assertEqual(response.status_code, 200)
    
    def test_endpoint_por_sector(self):
        """Prueba endpoint especial de estadísticas por sector"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/v1/clientes/por_sector/')
        self.assertEqual(response.status_code, 200)
