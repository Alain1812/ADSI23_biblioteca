import unittest
from . import BaseTestClass
from bs4 import BeautifulSoup
import datetime

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

    def test_reserva_copias_multiples(self):
        self.client.post('/login', data={'email': 'jhon@gmail.com', 'password': '123'})
        book_id = 12
        self.client.get(f'/reserve/book/{book_id}') 
        respuesta = self.client.get(f'/reserve/book/{book_id}')  
        self.assertNotEqual(respuesta.status_code, 20,
                                "Se permitió la reserva de múltiples copias del mismo libro.")

    def test_reservar_libro_no_disponible(self):
        self.client.post('/login', data={'email': 'james@gmail.com', 'password': '123456'})
        book_id = 321
        respuesta = self.client.get(f'/reserve/book/{book_id}')
        self.assertNotEqual(respuesta.status_code, 20, "Se permitió la reserva de un libro no disponible.")


    def test_tiempo_reserva_ilogico(self):
        self.client.post('/login', data={'email': 'james@gmail.com', 'password': '123456'})
        book_id = 123
        fecha_ilogica = '2005-01-01' 
        respuesta = self.client.get(f'/reserve/book/{book_id}?fecha={fecha_ilogica}')
        self.assertNotEqual(respuesta.status_code, 20, "Se permitió una reserva con un límite de tiempo ilógico.")
