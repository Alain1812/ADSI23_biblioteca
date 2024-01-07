from model import Connection, Book, User, ForumTopic, ForumPost, Reserva, Resena
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
        review_data = db.select("SELECT * FROM Resena WHERE libro_id = ?", (book_id,))

        # Crear una lista para almacenar objetos 'Review'
        reviews = []

        # Convertir cada resultado en un objeto 'Review' y agregarlo a la lista
        for rev in review_data:
            # Asumiendo que la clase 'Review' se inicializa como Review(id, book_id, user_id, rating, comment)
            reviews.append(Resena(rev[0], rev[1], rev[2], rev[3]))
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
        un_libro = db.select("SELECT * FROM Book WHERE title = ?", (titulo,))
        if len(un_libro) > 0:
            return "Libro ya existe"
        db.insert("INSERT INTO Book (title, author, cover, description) VALUES (?, ?, ?, ?)",
                  (titulo, author, cover, description))
        return "Libro agregado con éxito"

##  RECOMENDACIONES DE USUARIO
    def get_user_recommendations(self, user, number_of_books=100):
        """
        Método para obtener recomendaciones de libros para un usuario específico.
        :param user: El usuario para el cual se generarán las recomendaciones.
        :param number_of_books: Número de libros a recomendar.
        :return: Una lista de libros recomendados.
        """
        # Buscar en el historial de reservas del usuario
        print("Procesando Reservas:")
        user_reservations = db.select("SELECT * FROM Reserva WHERE emailUser = ?", (user.email,))
        print("Reservas de usuario:", user_reservations)

        if user_reservations:
            print("Buscando recomendaciones de libros")
            recommended_books = self.recommend_based_on_history(user_reservations, number_of_books, user.email)
        else:
            print("Sin reservas, recomendando varios libros al azar")
            recommended_books = self.select_random_books(number_of_books)

        # Si la cantidad de libros recomendados es menor que el número deseado, añade más libros al azar
        if len(recommended_books) < number_of_books:
            additional_books_needed = number_of_books - len(recommended_books)
            additional_books = self.select_random_books(additional_books_needed)
            recommended_books.extend(additional_books)

        return recommended_books

    def recommend_based_on_history(self, reservations, number_of_books, user_email):
        print("buscando...")

        related_users = self.get_related_users(reservations, 20, user_email)
        print("Usuarios relacionados 2:", related_users)

        if not related_users:
            related_books = self.select_random_books(number_of_books)
        else:
            book_ids = self.get_related_books(related_users, number_of_books, user_email)
            if not book_ids:
                related_books = self.select_random_books(number_of_books)
            else:
                # Convertir la lista de IDs de libros en una lista de objetos Book
                related_books = []
                for book_id in book_ids:
                    book_data = db.select("SELECT * FROM Book WHERE id = ?", (book_id,))
                    if book_data:
                        b = book_data[0]
                        book = Book(b[0], b[1], b[2], b[3], b[4])
                        related_books.append(book)

        return related_books

    def get_related_users(self, reservations, number_of_users, requesting_user_email):
        user_count_map = {}
        print("Sacando usuarios con gustos parecidos...")
        for reservation in reservations:
            book_id = reservation[2]
            users_who_reserved = self.get_users_who_reserved_book(book_id)
            print("Usuarios que han leido:", book_id)
            print("hola xd", users_who_reserved)
            for user_id in users_who_reserved:
                # Verificar si el usuario actual no es el usuario solicitante
                if user_id != requesting_user_email:
                    if user_id in user_count_map:
                        user_count_map[user_id] += 1
                    else:
                        user_count_map[user_id] = 1

        # Ordenar el hashmap por el contador
        related_users = sorted(user_count_map, key=user_count_map.get, reverse=True)
        print("Usuarios relacionados: ", related_users)

        # Tomar los primeros n usuarios o todos los disponibles si son menos que n
        return related_users[:min(len(related_users), number_of_users)]

    def get_users_who_reserved_book(self, book_id):
        # Consulta para obtener todos los usuarios que han reservado un libro específico
        users_data = db.select("SELECT emailUser FROM Reserva WHERE bookID = ?", (book_id,))
        return [user[0] for user in users_data]

    def get_related_books(self, related_users, number_of_books, requesting_user_email):
        book_count_map = {}

        for emailUser in related_users:
            books_reserved_by_user = self.get_books_reserved_by_user(emailUser)

            for book_id in books_reserved_by_user:
                # Verificar si el usuario solicitante no ha reservado el libro
                if not self.has_user_reserved_book(requesting_user_email, book_id):
                    if book_id in book_count_map:
                        book_count_map[book_id] += 1
                    else:
                        book_count_map[book_id] = 1

        # Ordenar el hashmap por el contador
        related_books = sorted(book_count_map, key=book_count_map.get, reverse=True)

        # Tomar los primeros n libros o todos los disponibles si son menos que n
        return related_books[:min(len(related_books), number_of_books)]

    def has_user_reserved_book(self, user_email, book_id):
        # Consulta para verificar si el usuario ha reservado el libro
        reservation_data = db.select("SELECT COUNT(*) FROM Reserva WHERE emailUser = ? AND bookID = ?",
                                     (user_email, book_id))
        return reservation_data[0][0] > 0

    def get_books_reserved_by_user(self, emailU):
        # Consulta para obtener todos los libros que un usuario ha reservado
        books_data = db.select("SELECT bookID FROM Reserva WHERE emailUser = ?", (emailU,))
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
        db.update("UPDATE Reserva SET fecha_fin = ? WHERE id = ?", (nueva_fecha_fin, reserva_id))


    def return_reserva(self, reserva_id):
        db.update("UPDATE Reserva SET estado = 'Finalizada' WHERE id = ?", (reserva_id,))


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

        db.update("UPDATE Reserva SET estado = 'Finalizada' WHERE fecha_reserva <= ? AND estado = 'Activa'",
                  (fecha_limite_str,))





    def add_or_update_review(self, user_email, book_id, review_text, rating):
        # Buscar si ya existe una reseña para este libro de este usuario
        existing_review = db.select("SELECT * FROM Resena WHERE email_user=? AND libro_id=?", (user_email, book_id))

        if existing_review:
            # Actualizar la reseña existente
            db.update("UPDATE Resena SET mensaje=?, puntuacion=? WHERE email_user=? AND libro_id=?",
                       (review_text, rating, user_email, book_id))
        else:
            # Crear una nueva reseña
            db.insert("INSERT INTO Resena (email_user, libro_id, mensaje, puntuacion) VALUES (?, ?, ?, ?)",
                       (user_email, book_id, review_text, rating))

    def get_reviews_by_book_id_and_user(self,user_email,book_id):
         res=db.select("SELECT * FROM Resena WHERE email_user=? AND libro_id=?", (user_email, book_id))
         final=None
         if res:
             final=Resena(res[0][0], res[0][1], res[0][2], res[0][3])
         return final


######RED DE AMIGOS#########
    def get_user_requests(self, user_email):
        # Conectar a la base de datos
        solicitudes = db.select("SELECT * FROM Solicitud WHERE email_solicitado = ?", (user_email,))
        listRequest = []
        for solicitud in solicitudes:
            listRequest.append(solicitud[0])
        return listRequest


    def get_usuarios(self, email_user):
        usuarios = db.select("SELECT email FROM User", ())
        amigos = self.get_amigos(email_user)
        listUsers = [usuario[0] for usuario in usuarios if usuario[0] != email_user and usuario[0] not in amigos]
        return listUsers


    def enviar_solicitud(self, emailSolicita, emailSolicitado):
        yaSolicitado = db.select("SELECT email_solicita from Solicitud WHERE email_solicitado= ?", (emailSolicitado,))
        if not yaSolicitado:
            db.insert("INSERT INTO Solicitud VALUES (?,?)", (emailSolicita, emailSolicitado))


    def aceptar_solicitud(self, user_email, email_solicitud):
        hayAmistad = db.select("SELECT * FROM Amistad WHERE email1 = ? and email2 = ?", (user_email, email_solicitud))
        if not hayAmistad:
            db.insert("INSERT INTO Amistad VALUES (?,?)", (user_email, email_solicitud))
            db.delete("DELETE FROM Solicitud WHERE email_solicitado = ? and email_solicita = ?",
                      (user_email, email_solicitud))
            db.delete("DELETE FROM Solicitud WHERE email_solicita = ? and email_solicitado = ?",
                      (user_email, email_solicitud))


    def rechazar_solicitud(self, user_email, email_solicitud):
        db.delete("DELETE FROM Solicitud WHERE email_solicitado = ? and email_solicita = ?", (user_email, email_solicitud))
        db.delete("DELETE FROM Solicitud WHERE email_solicita = ? and email_solicitado = ?", (user_email, email_solicitud))


    def get_amigos(self, user_email):
        amigos = db.select("SELECT * FROM Amistad WHERE email1 = ? or email2 = ?", (user_email, user_email))
        listAmigos = []
        for amigo in amigos:
            if amigo[0] == user_email:
                listAmigos.append(amigo[1])
            else:
                listAmigos.append(amigo[0])
        return listAmigos


    def eliminar_amigo(self, user_email,email_amigo):
        amigo = db.delete("DElETE FROM Amistad WHERE email1 = ? and email2 = ?", (user_email, email_amigo))
        amigo = db.delete("DElETE FROM Amistad WHERE email1 = ? and email2 = ?", (email_amigo, user_email))

    def obtener_nombre(self, user_email):
            result = db.select("SELECT name FROM User WHERE email=?", (user_email,))
            if result:
                return result[0][0]  # Extrae el primer elemento de la primera tupla si hay resultados
            else:
                return None  # O algún valor predeterminado que desees devolver si no se encuentra el nombre

    def get_user_reviews(self,user_email):
         res=db.select("SELECT * FROM Resena WHERE email_user=?", (user_email,))
         resenas = []
         for resena in res:
             resenas.append({
                 'libro_id': resena[1],
                 'mensaje': resena[2],
                 'puntuacion': resena[3],
             })
         return resenas

    def search_users(self, query="", limit=6, page=0):
        count = db.select("""
            SELECT count() 
            FROM User
            WHERE email LIKE ? 
        """, (f"%{query}%",))[0][0]

        res = db.select("""
            SELECT * 
            FROM User
            WHERE email LIKE ? 
            LIMIT ? OFFSET ?
        """, (f"%{query}%", limit, limit * page))

        users = [
            User(u[0], u[1], u[2])  # Ajusta según la estructura de tu tabla User
            for u in res
        ]

        return users, count
