from .Connection import Connection
from .Book import Book

db = Connection()

class Resena:
    def __init__(self, email_user, libro_id, resena, puntuacion):
        self.email_user = email_user
        self.libro = libro_id
        self.resena = resena
        self.puntuacion = puntuacion

        @property
        def libro(self):
            if type(self._libro) == int:
                b = db.select("SELECT * from Book WHERE id=?", (self._libro,))[0]
                self._libro = Book(b[0], b[1], b[2], b[3], b[4])
            return self._libro

        @libro.setter
        def libro(self, valor):
            self._libro = valor

