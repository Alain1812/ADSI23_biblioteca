import sqlite3


class ForumTopic:
    def __init__(self, id, title, emailUser, created_at):
        self.id = id
        self.title = title
        self.emailUser = emailUser
        self.created_at = created_at

    @staticmethod
    def create_new_topic(title):
        conn = sqlite3.connect('datos.db')
        cur = conn.cursor()

        cur.execute("INSERT INTO ForumTopic (title) VALUES (?)", (title,))
        conn.commit()
        conn.close()


    @property
    def user(self):
        if type(self._user) == str:
            t = db.select("SELECT * FROM User WHERE email = ?", (self._user,))[0]
            self._user = User(t[0], t[1], t[3])
        return self._user

    @user.setter
    def user(self, value):
        self._user = value

