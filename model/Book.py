from .Connection import Connection
from .Author import Author

db = Connection()

class Book:
    def __init__(self, id, title, author, cover, description):
        self.id = id
        self.title = title
        self.author = author
        self.cover = cover
        self.description = description

    @property
    def author(self):
        if type(self._author) == int:
            em = db.select("SELECT * from Author WHERE id=?", (self._author,))[0]
            self._author = Author(em[0], em[1])
        return self._author

    @author.setter
    def author(self, value):
        self._author = value

    def __str__(self):
        return f"{self.title} ({self.author})"

    # Methods to handle book copies
    def add_copy(self, condition='good'):
        db.execute("INSERT INTO BookCopy (book_id, condition) VALUES (?, ?)", (self.id, condition))
        db.commit()

    def get_copies(self):
        return db.select("SELECT * FROM BookCopy WHERE book_id=?", (self.id,))

    def update_copy_status(self, copy_id, status):
        db.execute("UPDATE BookCopy SET status=? WHERE id=?", (status, copy_id))
        db.commit()
