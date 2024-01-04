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




