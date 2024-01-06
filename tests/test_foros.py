from . import BaseTestClass
from bs4 import BeautifulSoup

class TestForos(BaseTestClass):

    def test_listar_temas(self):
        res = self.client.get('/forums')
        self.assertEqual(200, res.status_code)
        page = BeautifulSoup(res.data, features="html.parser")
        # Asumiendo que los temas están en una lista o en un div con una clase específica
        temas = page.find_all('div', class_='clase-tema')  # Cambiar 'clase-tema' según tu estructura HTML
        self.assertGreater(len(temas), 0)

    def test_ver_mensajes_tema(self):
        res = self.client.get('/forums/1')  # Asume que hay un tema con id 1
        self.assertEqual(200, res.status_code)
        page = BeautifulSoup(res.data, features="html.parser")
        mensajes = page.find_all('div', class_='clase-mensaje')  # Cambiar 'clase-mensaje' según tu estructura HTML
        self.assertGreater(len(mensajes), 0)

    def test_escribir_en_tema(self):
        params = {
            'content': 'Este es un nuevo mensaje de prueba',
            'emailUser': 'test@example.com'  # Asume que se requiere 'emailUser'
        }
        res = self.client.post('/forums/1/reply', data=params)  # Asume que hay un tema con id 1
        self.assertEqual(200, res.status_code)
        # Puede que necesites verificar más allá del código de estado, como comprobar si el mensaje se ha añadido en la página
