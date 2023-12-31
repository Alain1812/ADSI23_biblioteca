import sqlite3

class Reserva:
    def __init__(self, id, emailUser, bookID, estado='Activa', fecha_reserva=None,
                     fecha_fin=None):
        self.id = id
        self.emailUser = emailUser
        self.bookID = bookID
        self.estado = estado  # 'Activa' o 'Finalizada'
        self.fecha_reserva = fecha_reserva
        self.fecha_fin = fecha_fin

    @staticmethod
    def create_new_reserva(fecha_fin):
        conn = sqlite3.connect('datos.db')
        cur = conn.cursor()
        cur.execute("INSERT INTO Reserva (fecha_fin) VALUES (?)", (fecha_fin,))
        conn.commit()
        conn.close()


    @property
    def user(self):
        if type(self._user) == str:
            r = db.select("SELECT * FROM User WHERE email = ?", (self._user,))[0]
            self._user = User(r[0], r[1], r[3])
        return self._user

    @user.setter
    def __str__(self):
        return (f"Reserva ID: {self.id}, User Email: {self.emailUser}, "
                f"Book ID: {self.bookID}, Estado: {self.estado}, "
                f"Fecha de Reserva: {self.fecha_reserva.strftime('%Y-%m-%d %H:%M:%S')}, "
                f"Fecha Fin: {self.fecha_fin.strftime('%Y-%m-%d %H:%M:%S') if self.fecha_fin else 'N/A'}")



