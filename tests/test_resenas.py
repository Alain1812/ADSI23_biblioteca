import os
import sqlite3
from . import BaseTestClass
from bs4 import BeautifulSoup


#Connection
salt = "library"
script_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(script_dir, '..', 'datos.db')
conexion = sqlite3.connect(db_path)
cursor = conexion.cursor()

#antes de hacer este test hay que descargarlo de github de 0 ya que otros tests pueden tocar la base de datos y con ello hacer que de error


class test_resenas (BaseTestClass):

    def test_resenassinlogear(self):
        res = self.client.get('/review/book/1')
        self.assertEqual(200, res.status_code)

    def test_resenaslogeado(self):
        self.login('ejemplo@gmail.com', '123456')
        res = self.client.get('/review/book/1')
        self.assertEqual(200, res.status_code)

    def test_resenassinlibro(self):
        res = self.client.get('/review/book/999999')
        self.assertEqual(302, res.status_code)

    def test_puntuarsinlogear(self):
        res = self.client.get('/review/rate/1')
        self.assertEqual(302, res.status_code)

    def test_puntuarlogeado(self):
        self.login('ejemplo@gmail.com', '123456')
        res = self.client.get('/review/rate/1')
        self.assertEqual(200, res.status_code)


    def test_noresenas(self):
        cursor.execute(f"""DELETE FROM Resena WHERE libro_id = '1' """)
        conexion.commit()
        res = self.client.get('/review/book/1')
        page = BeautifulSoup(res.data, features="html.parser")
        self.assertEqual(0, len(page.find('div', id='reviews').find_all('div', class_='review')))

    def test_anadirresena(self):
        self.login('jhon@gmail.com', '123')
        cursor.execute(f"""DELETE FROM Resena WHERE libro_id = '1' """)
        conexion.commit()
        cursor.execute(f"""INSERT INTO Resena (email_user, libro_id, mensaje, puntuacion) VALUES ('jhon@gmail.com', 1, 'Me encantó este libro, los personajes y la trama eran increíbles. ¡Muy recomendado!', 4.5)""")
        conexion.commit()
        res = self.client.get('/review/book/1')
        page = BeautifulSoup(res.data, features="html.parser")
        self.assertEqual(1, len(page.find('div', id='reviews').find_all('div', class_='review')))


    def test_borrarresena(self):
        self.login('jhon@gmail.com', '123')
        cursor.execute(f"""DELETE FROM Resena WHERE libro_id = '1'""")
        conexion.commit()
        cursor.execute(f"""INSERT INTO Resena (email_user, libro_id, mensaje, puntuacion) VALUES ('jhon@gmail.com', 1, 'Me encantó este libro, los personajes y la trama eran increíbles. ¡Muy recomendado!', 9.5)""")
        conexion.commit()
        cursor.execute(f"""INSERT INTO Resena (email_user, libro_id, mensaje, puntuacion) VALUES ('ejemplo@gmail.com', 1, 'Malo', 2.5)""")
        conexion.commit()
        res = self.client.get('/review/book/1')
        page = BeautifulSoup(res.data, features="html.parser")
        self.assertEqual(2, len(page.find('div', id='reviews').find_all('div', class_='review')))
        cursor.execute(f"""DELETE FROM Resena WHERE email_user='jhon@gmail.com' AND libro_id = '1'  """)
        conexion.commit()
        res = self.client.get('/review/book/1')
        page = BeautifulSoup(res.data, features="html.parser")
        self.assertEqual(1, len(page.find('div', id='reviews').find_all('div', class_='review')))
