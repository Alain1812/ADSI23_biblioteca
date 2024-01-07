import unittest
from . import BaseTestClass
from bs4 import BeautifulSoup

class TestAdministrador(BaseTestClass):

    def test_acceso_administrador(self):
        self.client.post('/login', data={'email': 'admin@gmail.com', 'password': '123456'})
        respuesta = self.client.get('/admin')
        self.assertEqual(respuesta.status_code, 200, "Acceso denegado a la ruta del administrador.")
        pagina = BeautifulSoup(respuesta.data, 'html.parser')
        control_administrador = pagina.find('head', string='Control administrador')
        self.assertIsNotNone(control_administrador, "El contenido específico de administrador no está presente.")

    def test_crear_usuario(self):
        self.client.post('/login', data={'email': 'admin@gmail.com', 'password': '123456'})
        nuevo_usuario = {
            'username': 'nuevoUsuario',
            'email': 'nuevo@ejemplo.com',
            'password': 'contraseñaSegura',
            'admin': False
        }
        respuesta = self.client.post('/ruta_para_agregar_usuario', data=nuevo_usuario)
        self.assertEqual(respuesta.status_code, 200, "Error al crear un nuevo usuario.")

    def test_eliminar_usuario(self):
        self.client.post('/login', data={'email': 'admin@gmail.com', 'password': '123456'})
        usuario_a_eliminar = {
            'emailEliminar': 'ejemplo@gmail.com'
        }
        respuesta = self.client.post('/ruta_para_eliminar_usuario', data=usuario_a_eliminar)
        self.assertEqual(respuesta.status_code, 200, "Error al eliminar el usuario.")
