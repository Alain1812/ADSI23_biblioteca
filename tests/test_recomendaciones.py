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

class test_recomendaciones(BaseTestClass):


    def test_recomendaciones_sin_usuario(self):
        res = self.client.get('/recomendaciones')
        # Devuelve un error ya que no puede hacer recomendaciones sin estár logeado
        self.assertEqual(500, res.status_code)

    def test_recomendaciones_con_usuario(self):
        self.login('ejemplo@gmail.com', '123456')
        res = self.client.get('/recomendaciones')
        # Debe encontrar la página
        self.assertEqual(200, res.status_code)

    def test_recomendaciones_totales(self):
        self.login('ejemplo@gmail.com', '123456')
        total_books = 0
        current_page = 1
        total_pages = 4  # Calculado como 20 libros / 6 libros por página

        while current_page <= total_pages:
            res = self.client.get(f'/recomendaciones?page={current_page}')
            page = BeautifulSoup(res.data, features="html.parser")
            total_books += len(page.find_all('div', class_='card'))
            current_page += 1

        self.assertEqual(total_books, 20, "El número total de libros recomendados debe ser 20")

    def test_recomendaciones_cambio_historial(self):
        self.login('ejemplo@gmail.com', '123456')
        # Simular cambios en el historial de reservas (insertar datos de prueba en la base de datos)
        cursor.execute("""INSERT INTO Reserva (emailUser, bookID, estado, fecha_reserva, fecha_fin) VALUES ('ejemplo@gmail.com', 2, 'Activa', '2021-01-01', '2021-01-10')""")
        conexion.commit()
        res = self.client.get('/recomendaciones')
        page = BeautifulSoup(res.data, features="html.parser")
        self.assertEqual(len(page.find_all('div', class_='card')), 6)
        self.assertEqual(total_books, 20, "El número total de libros recomendados debe ser 20")

    def test_recomendaciones_no_en_historial(self):
        self.login('ejemplo@gmail.com', '123456')
        libros_reservados_ids = self.obtener_libros_reservados_ids('ejemplo@gmail.com')

        libros_recomendados_ids = []
        for page_num in range(1, 5):  # Para 4 páginas de recomendaciones
            res = self.client.get(f'/recomendaciones?page={page_num}')
            page = BeautifulSoup(res.data, features="html.parser")
            libros_recomendados = page.find_all('div', class_='card')
            libros_recomendados_ids.extend([self.extract_book_id(libro) for libro in libros_recomendados])

        # Verificar que ninguno de los libros recomendados esté en el historial de reservas
        for libro_id in libros_recomendados_ids:
            self.assertNotIn(libro_id, libros_reservados_ids,
                             "Un libro recomendado está en el historial de reservas del usuario")

    def obtener_libros_reservados_ids(self, email_usuario):
        cursor = conexion.cursor()
        cursor.execute("SELECT COUNT(*) FROM Reserva WHERE emailUser = ?", (email_usuario,))
        count = cursor.fetchone()[0]

        if count == 0:
            print("No hay reservas para este usuario.")
            return []

        cursor.execute("SELECT bookID FROM Reserva WHERE emailUser = ?", (email_usuario,))
        reservas = cursor.fetchall()
        return [reserva[0] for reserva in reservas]


    def extract_book_id(self, libro_div):
        enlace = libro_div.find('a', href=True)
        if enlace:
            # Suponiendo que el URL es algo como '/review/book/1'
            return enlace['href'].split('/')[-1]
        return None

    def tearDown(self):
        # Limpiar cualquier dato insertado en la base de datos para evitar afectar otras pruebas
        #cursor.execute("""DELETE FROM Reserva WHERE emailUser = 'ejemplo@gmail.com'""")
        conexion.commit()
        # Asegúrate de cerrar sesión si es necesario



# Agrega aquí cualquier método adicional que necesites, como login, logout, etc., si no están ya en BaseTestClass
