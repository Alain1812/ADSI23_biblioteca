import os
import sqlite3
from . import BaseTestClass
from bs4 import BeautifulSoup

# Conexión
salt = "library"
script_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(script_dir, '..', 'datos.db')
conexion = sqlite3.connect(db_path)
cursor = conexion.cursor()

class TestRedAmigos(BaseTestClass):


    def test_ver_solicitudes_pendientes(self):
        emailSolicita = "james@gmail.com"
        emailSolicitado = "jhon@gmail.com"
        emailSolicitado2 = "amigo@ejemplo.com"

        # Insertar la solicitud antes de intentar aceptarla
        cursor.execute(f"""DELETE FROM Solicitud""")
        cursor.execute("INSERT INTO Solicitud (email_solicita, email_solicitado) VALUES (?, ?)",
                       (emailSolicita, emailSolicitado))
        cursor.execute("INSERT INTO Solicitud (email_solicita, email_solicitado) VALUES (?, ?)",
                       (emailSolicita, emailSolicitado2))
        conexion.commit()
        self.client.post('/login', data={'email': 'jhon@gmail.com', 'password': '123'})
        res = self.client.get('/solicitudes')
        page = BeautifulSoup(res.data, features="html.parser")
        self.assertEqual(1, len(page.find_all('div', class_='card mb-3')))

    def test_ver_amigos(self):
        email1 = "james@gmail.com"
        email2 = "jhon@gmail.com"
        cursor.execute(f"""DELETE FROM Amistad""")
        cursor.execute("INSERT INTO Amistad (email1, email2) VALUES (?, ?)",(email1, email2))
        conexion.commit()

        self.client.post('/login', data={'email': 'jhon@gmail.com', 'password': '123'})


        res = self.client.get('/amigos')
        page = BeautifulSoup(res.data, features="html.parser")

        #vemos como se genera un amigo en la vista
        self.assertEqual(1, len(page.find_all('div', class_='card-body')))

    def test_eliminar_amigo(self):
        email1 = "james@gmail.com"
        email2 = "jhon@gmail.com"
        cursor.execute(f"""DELETE FROM Amistad""")
        cursor.execute("INSERT INTO Amistad (email1, email2) VALUES (?, ?)",
                       (email1, email2))
        conexion.commit()

        # Realizar el inicio de sesión
        self.client.post('/login', data={'email': 'james@gmail.com', 'password': '123456'})
        print(cursor.execute(f"""SELECT * FROM Amistad""").fetchall())
        # Datos para eliminar la amistad
        datos_eliminar_amigo = {
            'email_amigo': 'jhon@gmail.com',
            'eliminar_amigo': True
        }
        # Enviar la solicitud de eliminar
        respuesta = self.client.post('/amigos', data=datos_eliminar_amigo)



        # Verificar que la amistad se haya eliminado
        res = cursor.execute("SELECT * FROM Amistad WHERE email1 = ? AND email2 = ?",
                             (email1, email2)).fetchall()

        self.assertEqual([], res)  # Verificar que no haya amistad en la consulta
        self.assertEqual(respuesta.status_code, 200, "Error al eliminar la amistad.")


    def test_aceptar_solicitud_amistad(self):
        emailSolicita = "james@gmail.com"
        emailSolicitado = "jhon@ejemplo.com"

        # Insertar la solicitud antes de intentar aceptarla
        cursor.execute(f"""DELETE FROM Solicitud""")
        cursor.execute("INSERT INTO Solicitud (email_solicita, email_solicitado) VALUES (?, ?)",
                       (emailSolicita, emailSolicitado))
        conexion.commit()
        # Verificar que se ha insertado
        #print(cursor.execute("SELECT * FROM Solicitud WHERE email_solicita = ? AND email_solicitado = ?",
                             #(emailSolicita, emailSolicitado)).fetchall())
        # Realizar el inicio de sesión
        self.client.post('/login', data={'email': 'james@gmail.com', 'password': '123456'})
        # Datos para aceptar la solicitud
        datos_aceptar_solicitud = {
            'email_solicitud': 'jhon@ejemplo.com',
            'aceptarSol': True
        }

        # Enviar la solicitud de aceptación
        respuesta = self.client.post('/solicitudes', data=datos_aceptar_solicitud)

        # Verificar que la solicitud se haya eliminado
        res = cursor.execute("SELECT * FROM Amistad WHERE email1 = ? AND email2 = ?",
                             (emailSolicita, emailSolicitado)).fetchall()

        self.assertEqual([('james@gmail.com', 'jhon@ejemplo.com')], res)  # Verificar que haya amistad en la consulta
        self.assertEqual(respuesta.status_code, 200, "Error al aceptar la solicitud de amistad.")

    def test_rechazar_solicitud_amistad(self):
        emailSolicita = "james@gmail.com"
        emailSolicitado = "jhon@gmail.com"

        # Insertar la solicitud antes de intentar rechazarla
        cursor.execute(f"""DELETE FROM Solicitud""")
        cursor.execute("INSERT INTO Solicitud (email_solicita, email_solicitado) VALUES (?, ?)", (emailSolicita, emailSolicitado))
        conexion.commit()

        # Realizar el inicio de sesión
        self.client.post('/login', data={'email': 'james@gmail.com', 'password': '123456'})

        # Datos para rechazar la solicitud
        datos_rechazar_solicitud = {
            'email_solicitud': 'jhon@gmail.com',  # Debería coincidir con el emailSolicitado
            'rechazarSol': 'Rechazar'
        }

        # Enviar la solicitud de rechazo
        respuesta = self.client.post('/solicitudes', data=datos_rechazar_solicitud)

        # Verificar que la solicitud se haya eliminado
        res = cursor.execute("SELECT * FROM Solicitud WHERE email_solicita = ? AND email_solicitado = ?",
                            (emailSolicita, emailSolicitado)).fetchall()

        self.assertEqual([], res)  # Verificar que no haya resultados en la consulta
        self.assertEqual(respuesta.status_code, 200, "Error al rechazar la solicitud de amistad.")

