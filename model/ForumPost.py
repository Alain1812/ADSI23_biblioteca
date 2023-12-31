import sqlite3


class ForumPost:
    def __init__(self, id, topic_id, emailUser, content, created_at):
        self.id = id
        self.topic_id = topic_id
        self.emailUser = emailUser
        self.content = content
        self.created_at = created_at

    def get_tema(self):
        tema = db.select("SELECT * FROM Tema WHERE id = ?", (self.topic_id,))
        if tema:
            return Tema(tema[0][0], tema[0][1], tema[0][2], tema[0][3])
        return None

    def get_user(self):
        user = db.select("SELECT * FROM User WHERE email = ?", (self.emailUser,))
        if user:
            return User(user[0][0], user[0][1], user[0][3])
        return None

