from . import BaseTestClass
from bs4 import BeautifulSoup

class TestForos(BaseTestClass):

    def test_ver_temas_foro(self):
        respuesta = self.client.get('/forums')
        self.assertEqual(respuesta.status_code, 200, "Error al acceder a los temas del foro.")


    def test_ver_mensajes_tema(self):
        tema_id = 1  
        respuesta = self.client.get(f'/forums/{tema_id}')
        self.assertEqual(respuesta.status_code, 200, "Error al acceder a los mensajes del tema.")



    def test_crear_tema_foro(self):

        datos_tema_nuevo = {'title': 'Tema de prueba'}
        respuesta = self.client.post('/forums/new', data=datos_tema_nuevo)
        self.assertEqual(respuesta.status_code, 302, "Error o no redirige tras crear un tema nuevo.")


    def test_responder_tema_foro(self):
        tema_id = 1
        datos_respuesta = {'content': 'Respuesta de prueba'}
        respuesta = self.client.post(f'/forums/{tema_id}/reply', data=datos_respuesta)
        self.assertEqual(respuesta.status_code, 302, "Error o no redirige tras responder en un tema.")
