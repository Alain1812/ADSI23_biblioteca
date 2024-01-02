import hashlib
import os
import sqlite3
import json

salt = "library"
script_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(script_dir, '..', 'datos.db')


usuarios_path = os.path.join(script_dir, '..', 'usuarios.json')
temas_path = os.path.join(script_dir, '..', 'temas.json')
comentarios_path = os.path.join(script_dir, '..', 'comentarios.json')
resenas_path = os.path.join(script_dir, '..', 'resenas.json')
reservas_path = os.path.join(script_dir, '..', 'reservas.json')


con = sqlite3.connect(db_path)
cur = con.cursor()


### Create tables
cur.execute("""
	CREATE TABLE Author(
		id integer primary key AUTOINCREMENT,
		name varchar(40)
	)
""")

cur.execute("""
	CREATE TABLE Book(
		id integer primary key AUTOINCREMENT,
		title varchar(50),
		author integer,
		cover varchar(50),
		description TEXT,
		FOREIGN KEY(author) REFERENCES Author(id)
	)
""")

cur.execute("""
    CREATE TABLE User(
        id integer primary key AUTOINCREMENT,
        name varchar(20),
        email varchar(30),
        password varchar(32),
        admin int(1)
    )
""")


cur.execute("""
	CREATE TABLE Session(
		session_hash varchar(32) primary key,
		user_id integer,
		last_login float,
		FOREIGN KEY(user_id) REFERENCES User(id)
	)
""")

cur.execute("""
    CREATE TABLE ForumTopic(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        emailUser varchar(30),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (emailUser) REFERENCES User(email)
    )
""")

cur.execute("""
    CREATE TABLE ForumPost(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        topic_id INTEGER NOT NULL,
        emailUser varchar(30),
        content TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (topic_id) REFERENCES ForumTopic(id),
        FOREIGN KEY (emailUser) REFERENCES User(email)
    )
""")


cur.execute("""
    CREATE TABLE Resena (
    	email_user varchar(100),
    	libro_id integer,
    	mensaje text,
    	puntuacion float,
    	PRIMARY KEY(email_user, libro_id),
    	FOREIGN KEY(email_user) REFERENCES User(email),
    	FOREIGN KEY (libro_id) REFERENCES Book(id)
	)
""")

cur.execute("""
    CREATE TABLE Reserva(
    	id integer primary key AUTOINCREMENT,
		emailUser	varchar(30) NOT NULL,
		bookID	INTEGER NOT NULL,
		estado	TEXT DEFAULT 'Activa',
		fecha_reserva	TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
		fecha_fin	TIMESTAMP,
		FOREIGN KEY(bookID) REFERENCES Book(id),
		FOREIGN KEY(emailUser) REFERENCES User(email)
    )
""")
####RED DE AMIGOS####

cur.execute("""
	CREATE TABLE Amistad(
		email1 varchar(30),
		email2 varchar(30),
		PRIMARY KEY(email1, email2),
		FOREIGN KEY(email1) REFERENCES User(email)
	)
""")
cur.execute("""
    CREATE TABLE Solicitud(
		email_solicita varchar(30),
		email_solicitado varchar(30),
		PRIMARY KEY(email_solicita, email_solicitado),
		FOREIGN KEY(email_solicita) REFERENCES User(email)
    )
""")

### Insert JSON

with open('../reservas.json', 'r') as f:
	reservas = json.load(f)['reservas']

with open(temas_path, 'r', encoding='utf-8') as f:
	temas = json.load(f)['temas']

with open(comentarios_path, 'r', encoding='utf-8') as f:
	comentarios = json.load(f)['comentarios']

with open( resenas_path, 'r', encoding='utf-8') as f:
	resenas = json.load(f)['resenas']

with open('../usuarios.json', 'r') as f:
	usuarios = json.load(f)['usuarios']

for user in usuarios:
	dataBase_password = user['password'] + salt
	hashed = hashlib.md5(dataBase_password.encode())
	dataBase_password = hashed.hexdigest()
	cur.execute("INSERT INTO User (name, email, password, admin) VALUES (?, ?, ?, ?)",(user['nombres'], user['email'], dataBase_password, user['admin']))

	con.commit()

for resena in resenas:
    cur.execute(
        "INSERT INTO Resena (email_user, libro_id, mensaje, puntuacion) VALUES (?, ?, ?, ?)",
        (resena['emailUser'], resena['libro_id'], resena['resena'], resena['puntuacion'])
    )
    con.commit()

for reserva in reservas:
	cur.execute("INSERT INTO Reserva (id, emailUser, bookID, estado, fecha_reserva, fecha_fin) VALUES (?, ?, ?, ?, ?, ?)",
                (reserva['id'], reserva['emailUser'], reserva['bookID'], reserva['estado'], reserva['fecha_reserva'], reserva['fecha_fin']))
	con.commit()

for tema in temas:
    # Asegúrate de que los nombres de las claves en el JSON coincidan con estos
    title = tema['titulo']
    emailUser = tema['emailUser']
    created_at = tema['created_at']

    # Insertar el tema en la base de datos
    cur.execute("INSERT INTO ForumTopic (title, emailUser, created_at) VALUES (?, ?, ?)",
                (title, emailUser, created_at))
    con.commit()

for comentario in comentarios:
	cur.execute(f"""INSERT INTO ForumPost VALUES ('{comentario['id']}', '{comentario['topic_id']}', '{comentario['emailUser']}', '{comentario['content']}', '{comentario['created_at']}')""")
	con.commit()


#### Insert books
with open('../libros.tsv', 'r', encoding='utf-8') as f:
    libros = [x.split("\t") for x in f.readlines()]

for author, title, cover, description in libros:
	res = cur.execute(f"SELECT id FROM Author WHERE name=\"{author}\"")
	if res.rowcount == -1:
		cur.execute(f"""INSERT INTO Author VALUES (NULL, \"{author}\")""")
		con.commit()
		res = cur.execute(f"SELECT id FROM Author WHERE name=\"{author}\"")
	author_id = res.fetchone()[0]

	cur.execute("INSERT INTO Book VALUES (NULL, ?, ?, ?, ?)",
		            (title, author_id, cover, description.strip()))

	con.commit()
