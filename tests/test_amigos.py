import unittest
from . import BaseTestClass
from bs4 import BeautifulSoup

class TestRedAmigos(BaseTestClass):

    def test_solicitar_amistad(self):
        self.client.post('/login', data={'email': 'james@gmail.com', 'password': '123456'})
        datos_solicitud_amistad = {
            'email_amigo': 'jhon@gmail.com'
        }
        respuesta = self.client.post('/verUsuarios', data=datos_solicitud_amistad)
        self.assertEqual(respuesta.status_code, 200, "Error al enviar la solicitud de amistad.")

    def test_ver_solicitudes_pendientes(self):
        self.client.post('/login', data={'email': 'james@gmail.com', 'password': '123456'})
        respuesta = self.client.get('/solicitudes')
        self.assertEqual(respuesta.status_code, 200, "Error al acceder a la página de solicitudes.")

    def test_aceptar_solicitud_amistad(self):
        self.client.post('/login', data={'email': 'james@gmail.com', 'password': '123456'})
        datos_aceptar_solicitud = {
            'email_solicitud': 'amigo@ejemplo.com',
            'aceptarSol': 'Aceptar'
        }
        respuesta = self.client.post('/solicitudes', data=datos_aceptar_solicitud)
        self.assertEqual(respuesta.status_code, 200, "Error al aceptar la solicitud de amistad.")

    def test_rechazar_solicitud_amistad(self):
        self.client.post('/login', data={'email': 'james@gmail.com', 'password': '123456'})
        datos_rechazar_solicitud = {
            'email_solicitud': 'amigo@ejemplo.com',
            'rechazarSol': 'Rechazar'
        }
        respuesta = self.client.post('/solicitudes', data=datos_rechazar_solicitud)
        self.assertEqual(respuesta.status_code, 200, "Error al rechazar la solicitud de amistad.")
