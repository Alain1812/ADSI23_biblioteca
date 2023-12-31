from model import Connection, Book, User, ForumTopic, ForumPost, Reserva
from model.tools import hash_password
from datetime import timedelta


db = Connection()

class LibraryController:
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super(LibraryController, cls).__new__(cls)
            cls.__instance.__initialized = False
        return cls.__instance


    def search_books(self, title="", author="", limit=6, page=0):
        count = db.select("""
				SELECT count() 
				FROM Book b, Author a 
				WHERE b.author=a.id 
					AND b.title LIKE ? 
					AND a.name LIKE ? 
		""", (f"%{title}%", f"%{author}%"))[0][0]
        res = db.select("""
				SELECT b.* 
				FROM Book b, Author a 
				WHERE b.author=a.id 
					AND b.title LIKE ? 
					AND a.name LIKE ? 
				LIMIT ? OFFSET ?
		""", (f"%{title}%", f"%{author}%", limit, limit * page))
        books = [
            Book(b[0], b[1], b[2], b[3], b[4])
            for b in res
        ]
        return books, count

    def get_user(self, email, password):
        user = db.select("SELECT id, name, email, admin from User WHERE email = ? AND password = ?",
                         (email, hash_password(password)))
        if len(user) > 0:
            is_admin = True if user[0][3] == 1 else False
            return User(user[0][0], user[0][1], user[0][2], is_admin)
        else:
            return None

    def get_user_cookies(self, token, time):
        user = db.select(
            "SELECT u.* from User u, Session s WHERE u.id = s.user_id AND s.last_login = ? AND s.session_hash = ?",
            (time, token))
        if len(user) > 0:
            return User(user[0][0], user[0][1], user[0][2], user[0][4])
        else:
            return None

    def get_book_info(self, book_id):
        # Realizar una consulta a la base de datos para obtener la información del libro
        res = db.select("SELECT * FROM Book WHERE id = ?", (book_id,))
        if len(res) > 0:
            # Convertir el resultado en un objeto 'Book'
            return Book(res[0][0], res[0][1], res[0][2], res[0][3], res[0][4])
        else:
            return None

    def get_reviews_by_book_id(self, book_id):
        # Realizar una consulta a la base de datos para obtener las reseñas del libro
        reviews_data = db.select("SELECT * FROM Review WHERE libro_id = ?", (book_id,))

        # Crear una lista para almacenar objetos 'Review'
        reviews = []

        # Convertir cada resultado en un objeto 'Review' y agregarlo a la lista
        for review in reviews_data:
            # Asumiendo que la clase 'Review' se inicializa como Review(id, book_id, user_id, rating, comment)
            reviews.append(Review(review[0], review[1], review[2], review[3], review[4]))

        return reviews

    def list_topics(self):
        res = db.select("SELECT * FROM ForumTopic")
        topics = [ForumTopic(t[0], t[1], t[2], t[3]) for t in res]
        return topics

    def show_topic(self, topic_id):
        topic_res = db.select("SELECT * FROM ForumTopic WHERE id = ?", (topic_id,))
        topic = None
        if topic_res:
            t = topic_res[0]
            topic = ForumTopic(t[0], t[1], t[2], t[3])

        replies_res = db.select("SELECT * FROM ForumPost WHERE topic_id = ?", (topic_id,))
        replies = [ForumPost(p[0], p[1], p[2], p[3], p[4]) for p in replies_res]

        return topic, replies

    def create_topic(self, title, emailUser):
        # Realizar la inserción en la base de datos
        db.insert("INSERT INTO ForumTopic (title, emailUser, created_at) VALUES (?, ?, datetime('now'))",
                  (title, emailUser))

    def post_reply(self, topic_id, emailUser, content):
        db.insert("INSERT INTO ForumPost (topic_id, emailUser, content, created_at) VALUES (?, ?, ?, datetime('now'))",
                  (topic_id, emailUser, content))

    def agregar_usuario(self, name, email, password, admin):
        usuario_existente = db.select("SELECT * FROM User WHERE email = ?", (email,))
        if len(usuario_existente) > 0:
            return "Usuario ya existe"
        db.insert("INSERT INTO User (name, email, password, admin) VALUES (?, ?, ?, ?)",
                  (name, email, hash_password(password), admin))
        return "Usuario creado con éxito"

    def eliminar_usuario(self, email):
        usuario_existente = db.select("SELECT * FROM User WHERE email = ?", (email,))
        if len(usuario_existente) == 0:
            return "Usuario no encontrado"
        db.delete("DELETE FROM User WHERE email = ?", (email,))
        return "Usuario eliminado con éxito"

    def get_libro(self, titulo):
        res = db.select("SELECT * FROM Book WHERE title = ?", (titulo,))
        if len(res) > 0:
            return Book(res[0][0], res[0][1], res[0][2], res[0][3], res[0][4])
        else:
            return None

    def agregar_libro(self, titulo, author, cover, description):
        unLibro = self.get_libro(titulo)
        if unLibro:
            return "Libro ya existe"
        db.insert("INSERT INTO Book (title, author, cover, description) VALUES (?, ?, ?, ?)",
                  (titulo, author, cover, description))
        return "Libro agregado con éxito"

    def get_admin(self, email, password):
        admin = db.select("SELECT * from Admin WHERE email = ? AND password = ?", (email, hash_password(password)))
        if len(admin) > 0:
            return Admin(admin[0][0], admin[0][1], admin[0][2])
        else:
            return None

    def save_reservation(user_id, book_id, start_date, end_date):
        try:
            # Convertir las fechas de cadena a objetos datetime
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
        except ValueError as ve:
            # Error de formato de fecha
            return {"success": False, "message": f"Error en el formato de la fecha: {ve}"}

        try:
            # Conectar a la base de datos
            conn = sqlite3.connect("datos.db", check_same_thread=False)
            cursor = conn.cursor()

            # Comprobar si el libro está disponible
            cursor.execute("SELECT COUNT(*) FROM Reserva WHERE ID_Libro = ? AND Estado = 'Activa'", (book_id,))
            if cursor.fetchone()[0] > 0:
                return {"success": False, "message": "El libro ya está reservado."}

            # Comprobar si el usuario ya tiene 3 reservas
            cursor.execute("SELECT COUNT(*) FROM Reserva WHERE ID_Usuario = ? AND Estado = 'Activa'", (user_id,))
            if cursor.fetchone()[0] >= 3:
                return {"success": False, "message": "El usuario ya tiene 3 reservas activas."}

            # Insertar la reserva en la base de datos
            cursor.execute(
                "INSERT INTO Reserva (ID_Usuario, ID_Libro, Estado, Fecha_Reserva, Fecha_Vencimiento) VALUES (?, ?, 'Activa', ?, ?)",
                (user_id, book_id, start_date, end_date))
            conn.commit()

        except sqlite3.Error as e:
            # Error de base de datos
            return {"success": False, "message": f"Error en la base de datos: {e}"}

        finally:
            conn.close()

        return {"success": True, "message": "Reserva realizada con éxito."}

    def get_user_recommendations(self, user, number_of_books=5):
        """
        Método para obtener recomendaciones de libros para un usuario específico.
        :param user: El usuario para el cual se generarán las recomendaciones.
        :param number_of_books: Número de libros a recomendar.
        :return: Una lista de libros recomendados.
        """
        # Buscar en el historial de reservas del usuario
        print("Procesando Reservas:")
        user_reservations = db.select("SELECT * FROM Reserva WHERE ID_Usuario = ?", (user.id,))
        print("Reservas de usuario:", user_reservations)

        if user_reservations:
            print("Buscando recomendaciones de libros")
            recommended_books = self.recommend_based_on_history(user_reservations, 6)
        else:
            print("Sin reservas, recomendando varios libros al azar")
            recommended_books = self.select_random_books(5)
        return recommended_books

    def recommend_based_on_history(self, reservations, number_of_books):

        # Usar el método get_related_users para obtener usuarios relacionados

        related_users = self.get_related_users(reservations, 10)
        print("Usuarios relacionados:", related_users)
        if not related_users:
            related_books= self.select_random_books(number_of_books)
        else:
            related_books = self.get_related_books(related_users, number_of_books)
            if not related_books:
                related_books = self.select_random_books(number_of_books)
        """books = [
            Book(b[0], b[1], b[2], b[3], b[4])
            for b in related_books
        ]"""
        return related_books

    def get_related_users(self, reservations, number_of_users):
        user_count_map = {}

        for reservation in reservations:
            book_id = reservation['ID_Libro']
            users_who_reserved = self.get_users_who_reserved_book(book_id)

            for user_id in users_who_reserved:
                if user_id in user_count_map:
                    user_count_map[user_id] += 1
                else:
                    user_count_map[user_id] = 1

        # Ordenar el hashmap por el contador
        related_users = sorted(user_count_map, key=user_count_map.get, reverse=True)

        # Tomar los primeros n usuarios o todos los disponibles si son menos que n
        return related_users[:min(len(related_users), number_of_users)]

    def get_users_who_reserved_book(self, book_id):
        # Consulta para obtener todos los usuarios que han reservado un libro específico
        users_data = db.select("SELECT ID_Usuario FROM Reserva WHERE ID_Libro = ?", (book_id,))
        return [user[0] for user in users_data]

    def get_related_books(self, related_users, number_of_books):
        book_count_map = {}

        for user_id in related_users:
            books_reserved_by_user = self.get_books_reserved_by_user(user_id)

            for book_id in books_reserved_by_user:
                if book_id in book_count_map:
                    book_count_map[book_id] += 1
                else:
                    book_count_map[book_id] = 1

        # Ordenar el hashmap por el contador
        related_books = sorted(book_count_map, key=book_count_map.get, reverse=True)

        # Tomar los primeros n libros o todos los disponibles si son menos que n
        return related_books[:min(len(related_books), number_of_books)]

    def get_books_reserved_by_user(self, user_id):
        # Consulta para obtener todos los libros que un usuario ha reservado
        books_data = db.select("SELECT ID_Libro FROM Reserva WHERE ID_Usuario = ?", (user_id,))
        return [book[0] for book in books_data]

    def select_random_books(self, number_of_books):
        """
        Método para seleccionar una cantidad determinada de libros al azar.
        """
        res = db.select("SELECT * FROM Book ORDER BY RANDOM() LIMIT ?", (number_of_books,))
        books = [
            Book(b[0], b[1], b[2], b[3], b[4])
            for b in res
        ]
        return books



#RESERVAS

    def create_reserva(self, emailUser, book_id, start_date, end_date):
        try:
            # Insertar la reserva en la base de datos
            db.insert("INSERT INTO Reserva (emailUser, bookID, estado, fecha_reserva, fecha_fin) VALUES (?, ?, ?, ?, ?)",
                      (emailUser, book_id, 'Activa', start_date, end_date))
            return 'Reserva realizada con éxito', True
        except Exception as e:
            return f'Ocurrió un error al procesar su reserva: {e}', False


    def get_user_reservas(self, emailUser):
        reservas_raw = db.select("SELECT * FROM Reserva WHERE emailUser = ?", (emailUser,))
        reservas = []
        for reserva in reservas_raw:
            reservas.append({
                'id': reserva[0],
                'emailUser': reserva[1],
                'bookID': reserva[2],
                'estado': reserva[3],
                'fecha_reserva': reserva[4],
                'fecha_fin': reserva[5]
            })
        return reservas


    def get_reserva_details(self, reserva_id):
        detalles_reserva_raw = db.select("SELECT * FROM Reserva WHERE id = ?", (reserva_id,))
        if detalles_reserva_raw:
            detalle = detalles_reserva_raw[0]
            return {
                'id': detalle[0],
                'emailUser': detalle[1],
                'bookID': detalle[2],
                'estado': detalle[3],
                'fecha_reserva': detalle[4],
                'fecha_fin': detalle[5]
            }
        else:
            return None


    def update_reserva(self, reserva_id, nueva_fecha_fin):
        # Actualiza la fecha de finalización en la base de datos
        db.update("UPDATE Reserva SET fecha_fin = ? WHERE id = ?", (nueva_fecha_fin, reserva_id))


    def return_reserva(self, reserva_id):
        db.update("UPDATE Reserva SET estado = 'FINALIZADA' WHERE id = ?", (reserva_id,))


    def can_reserve_book(self, book_id):
        result = db.select("SELECT COUNT(*) FROM Reserva WHERE bookID = ? AND estado = 'Activa'", (book_id,))
        count = result[0][0] if result else 0
        return count < 3


    def can_user_reserve_book(self, emailUser, book_id):
        result = db.select("SELECT COUNT(*) FROM Reserva WHERE emailUser = ? AND bookID = ? AND estado = 'Activa'",
                           (emailUser, book_id))
        count = result[0][0] if result else 0
        return count == 0


    def can_user_make_more_reservations(self, emailUser):
        result = db.select("SELECT COUNT(*) FROM Reserva WHERE emailUser = ? AND estado = 'Activa'", (emailUser,))
        count = result[0][0] if result else 0
        return count < 5


    def actualizar_reservas_vencidas(self):
        from datetime import datetime, timedelta
        fecha_limite = datetime.now() - timedelta(days=60)
        fecha_limite_str = fecha_limite.strftime('%Y-%m-%d %H:%M:%S')

        # Usar db.update para ejecutar la sentencia SQL de actualización
        db.update("UPDATE Reserva SET estado = 'FINALIZADA' WHERE fecha_reserva <= ? AND estado = 'Activa'",
                  (fecha_limite_str,))


