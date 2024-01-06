import datetime
from .Connection import Connection
from .tools import hash_password
from model import User

class Admin(User):
    def __init__(self, id, username, email):
        super().__init__(id, username, email)