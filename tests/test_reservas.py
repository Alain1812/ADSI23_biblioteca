import unittest
from . import BaseTestClass
from bs4 import BeautifulSoup

class TestGestionReservas(BaseTestClass):

    def test_ver_historial_reservas(self):
        self.client.post('/login', data={'email': 'james@gmail.com', 'password': '123456'})
        respuesta = self.client.get('/mis_reservas')
        self.assertEqual(respuesta.status_code, 200, "Error al acceder al historial de reservas.")

    def test_reservar_libro(self):
        self.client.post('/login', data={'email': 'james@gmail.com', 'password': '123456'})
        book_id = 123
        respuesta = self.client.get(f'/reserve/book/{book_id}')
        self.assertEqual(respuesta.status_code, 200, "Error al acceder a la página de reserva de libro.")

    def test_devolver_libro(self):
        self.client.post('/login', data={'email': 'james@gmail.com', 'password': '123456'})
        reserva_id = 123
        respuesta = self.client.get(f'/reserve/return/{reserva_id}')
        self.assertEqual(respuesta.status_code, 302, "Error al devolver el libro.")
        self.assertTrue('Location' in respuesta.headers, "No se encontró la cabecera de redirección.")


