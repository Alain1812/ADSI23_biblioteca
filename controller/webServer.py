from .LibraryController import LibraryController
from flask import Flask, render_template, request, make_response, redirect , session, url_for
from model import User
from datetime import datetime, timedelta
import sqlite3

app = Flask(__name__, static_url_path='', static_folder='../view/static', template_folder='../view/')


library = LibraryController()


@app.before_request
def get_logged_user():
	if '/css' not in request.path and '/js' not in request.path:
		token = request.cookies.get('token')
		time = request.cookies.get('time')
		if token and time:
			request.user = library.get_user_cookies(token, float(time))
			if request.user:
				request.user.token = token


@app.after_request
def add_cookies(response):
	if 'user' in dir(request) and request.user and request.user.token:
		session = request.user.validate_session(request.user.token)
		response.set_cookie('token', session.hash)
		response.set_cookie('time', str(session.time))
	return response


@app.route('/')
def index():
	return render_template('index.html')


@app.route('/catalogue')
def catalogue():
	title = request.values.get("title", "")
	author = request.values.get("author", "")
	page = int(request.values.get("page", 1))
	books, nb_books = library.search_books(title=title, author=author, page=page - 1)
	total_pages = (nb_books // 6) + 1
	return render_template('catalogue.html', books=books, title=title, author=author, current_page=page,
	                       total_pages=total_pages, max=max, min=min)

@app.route('/recomendaciones')
def recommendations():
    if not request.user:
        return redirect(url_for('login'))

    page = int(request.values.get("page", 1))
    number_of_books_per_page = 6  # O el número que prefieras

    # Obtener las recomendaciones para el usuario
    recommended_books = library.get_user_recommendations(request.user)
    print("Libros recomendados:", recommended_books)

    # Calcular la paginación
    total_books = len(recommended_books)
    total_pages = (total_books // number_of_books_per_page) + (1 if total_books % number_of_books_per_page > 0 else 0)

    # Obtener los libros para la página actual
    start = (page - 1) * number_of_books_per_page
    end = start + number_of_books_per_page
    books_to_display = recommended_books[start:end]

    # Renderizar la plantilla con los libros recomendados para la página actual
    return render_template('recomendaciones.html', books=books_to_display, current_page=page, total_pages=total_pages, max=max, min=min)


@app.route('/login', methods=['GET', 'POST'])
def login():
	if 'user' in dir(request) and request.user and request.user.token:
		return redirect('/')
	email = request.values.get("email", "")
	password = request.values.get("password", "")
	user = library.get_user(email, password)
	if user:
		session = user.new_session()
		resp = redirect("/")
		resp.set_cookie('token', session.hash)
		resp.set_cookie('time', str(session.time))
	else:
		if request.method == 'POST':
			return redirect('/login')
		else:
			resp = render_template('login.html')
	return resp


@app.route('/logout')
def logout():
	path = request.values.get("path", "/")
	resp = redirect(path)
	resp.delete_cookie('token')
	resp.delete_cookie('time')
	if 'user' in dir(request) and request.user and request.user.token:
		request.user.delete_session(request.user.token)
		request.user = None
	return resp


@app.route('/forums')
def forums():
    topics = library.list_topics()
    return render_template('forum.html', topics=topics)

@app.route('/forums/<int:topic_id>')
def forum_topic(topic_id):
	topic, replies = library.show_topic(topic_id)  # Asegurarse de capturar ambos valores
	return render_template('topic.html', topic=topic, replies=replies)

@app.route('/forums/new', methods=['GET', 'POST'])
def new_forum_topic():
    if request.method == 'POST':
        title = request.form['title']
        if not hasattr(request, 'user') or not request.user:
            return redirect(url_for('login'))
        emailUser = request.user.email  # Obtener el correo electrónico desde el objeto user
        library.create_topic(title, emailUser)
        return redirect('/forums')
    return render_template('new_topic.html')

@app.route('/forums/<int:topic_id>/reply', methods=['POST'])
def post_reply(topic_id):
    content = request.form['content']
    if not hasattr(request, 'user') or not request.user:
        return redirect(url_for('login'))
    emailUser = request.user.email  # Obtener el correo electrónico desde el objeto user
    library.post_reply(topic_id, emailUser, content)
    return redirect(url_for('forum_topic', topic_id=topic_id))


@app.route('/admin', methods=['GET'])
def admin_page():
    return render_template('admin.html')  # Asumiendo que tu archivo HTML se llama 'admin.html'

@app.route('/ruta_para_agregar_usuario', methods=['POST'])
def agregar_usuario():
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']
    admin = request.form.get('admin', '0')
    admin_value = 1 if admin == '1' else 0
    resultado = library.agregar_usuario(username, email, password, admin_value)
    return render_template('resultado.html', mensaje=resultado)

@app.route('/ruta_para_eliminar_usuario', methods=['POST'])
def eliminar_usuario():
    emailEliminar = request.form['emailEliminar']
    resultado = library.eliminar_usuario(emailEliminar)
    return render_template('resultado.html', mensaje=resultado)

@app.route('/ruta_para_agregar_libro', methods=['POST'])
def agregar_libro():
    title = request.form['title']
    author = request.form['author']
    cover = request.form['cover']
    description = request.form['description']
    resultado = library.agregar_libro(title, author, cover, description)
    return render_template('resultado.html', mensaje=resultado)
	
@app.route('/review/book/<int:book_id>', methods=['GET'])
def review_book(book_id):
    # Obtener información del libro
    book_details = library.get_book_info(book_id)

    reviews, names = library.get_reviews_by_book_id(book_id)

    if book_details:
        # Renderizar 'resenas.html' con la información del libro, sus reseñas y nombres
        return render_template('resenas.html', book=book_details, reviews=reviews, names=names)
    else:
        # Manejar el caso en que el libro no se encuentre (p.ej., redirigir a una página de error)
        return redirect(url_for('book_not_found'))





#RESERVAS
@app.route('/reserve/book/<int:book_id>')
def reserve_book(book_id):
    book_info = library.get_book_info(book_id)
    if book_info is None:
        return "Libro no encontrado", 404

    if hasattr(request, 'user') and request.user:
        emailUser = request.user.email
    else:
        return redirect(url_for('login'))

    return render_template('new_reserva.html', book=book_info, emailUser=emailUser)


@app.route('/process_reservation', methods=['POST'])
def process_reservation():
    error_message = None
    if 'user' in dir(request) and request.user and request.user.token:
        emailUser = request.user.email
    else:
        error_message = 'No estás autenticado. Por favor, inicia sesión.'
        return render_template('login.html', error_message=error_message)

    book_id = request.form.get('book_id')
    start_date_str = request.form.get('startDate')
    end_date_str = request.form.get('endDate')

    try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        today = datetime.today().date()

        if start_date < today:
            error_message = "No se puede reservar para una fecha pasada."
            book_info = library.get_book_info(book_id)
            return render_template('new_reserva.html', error_message=error_message, book=book_info)

        if end_date < start_date:
            error_message = "La fecha de finalización no puede ser anterior a la fecha de inicio."
            book_info = library.get_book_info(book_id)
            return render_template('new_reserva.html', error_message=error_message, book=book_info)

        # Comprobar las restricciones de reserva
        if not library.can_reserve_book(book_id):
            error_message = 'Este libro ya ha alcanzado el límite máximo de reservas activas.'
        elif not library.can_user_reserve_book(emailUser, book_id):
            error_message = 'Ya tienes una reserva activa para este libro.'
        elif not library.can_user_make_more_reservations(emailUser):
            error_message = 'Has alcanzado el límite máximo de reservas activas.'
        elif (end_date - start_date).days > 60:
            error_message = 'La fecha de finalización no puede exceder los dos meses desde la fecha de inicio.'

        if error_message:
            book_info = library.get_book_info(book_id)
            return render_template('new_reserva.html', error_message=error_message, book=book_info)

        success = library.create_reserva(emailUser, book_id, start_date, end_date)
        if success:
            return redirect(url_for('mis_reservas'))
        else:
            error_message = 'Hubo un problema al procesar tu reserva.'
            book_info = library.get_book_info(book_id)
            return render_template('new_reserva.html', error_message=error_message, book=book_info)

    except ValueError as e:
        error_message = f"Error al procesar las fechas: {e}"
        book_info = library.get_book_info(book_id)
        return render_template('new_reserva.html', error_message=error_message, book=book_info)


@app.route('/mis_reservas')
def mis_reservas():
    error_message = None
    if 'user' in dir(request) and request.user and request.user.token:
        emailUser = request.user.email

        library.actualizar_reservas_vencidas()

        reservas_raw = library.get_user_reservas(emailUser)
        reservas = []
        for reserva in reservas_raw:
            libro_info = library.get_book_info(reserva['bookID'])
            if libro_info:
                reserva_modificada = {
                    'id': reserva['id'],
		            'bookID': libro_info.id,
                    'titulo_libro': libro_info.title,
                    'nombre_autor': libro_info.author,
                    'estado': reserva['estado'],
                    'fecha_reserva': reserva['fecha_reserva'],
                    'fecha_fin': reserva['fecha_fin']
                }
                reservas.append(reserva_modificada)
            else:
                error_message = "Error al cargar información de algunos libros."

        return render_template('mis_reservas.html', reservas=reservas, error_message=error_message)
    else:
        error_message = 'No estás autenticado. Por favor, inicia sesión.'
        return render_template('login.html', error_message=error_message)



@app.route('/reserve/details/<int:reserva_id>')
def reserva_details(reserva_id):
    error_message = None
    detalles_reserva = library.get_reserva_details(reserva_id)

    if detalles_reserva:
        libro_info = library.get_book_info(detalles_reserva['bookID'])
        if libro_info:
            detalles_reserva['titulo_libro'] = libro_info.title
            detalles_reserva['nombre_autor'] = libro_info.author.name
            detalles_reserva['descripcion_libro'] = libro_info.description
            detalles_reserva['portada_libro'] = libro_info.cover

            return render_template('reserva_details.html', detalles=detalles_reserva)
        else:
            error_message = "Error al cargar información del libro."
            return render_template('mis_reservas.html', error_message=error_message)
    else:
        error_message = 'No se encontraron detalles para la reserva solicitada.'
        return render_template('mis_reservas.html', error_message=error_message)


@app.route('/reserve/edit/<int:reserva_id>', methods=['GET', 'POST'])
def edit_reserva(reserva_id):
    detalles_reserva = library.get_reserva_details(reserva_id)
    error_message = None
    today = datetime.today().date()

    if request.method == 'POST':
        nueva_fecha_fin_str = request.form.get('fecha_fin')
        try:
            nueva_fecha_fin = datetime.strptime(nueva_fecha_fin_str, '%Y-%m-%d').date()
            fecha_reserva_str = detalles_reserva['fecha_reserva']
            fecha_reserva = datetime.strptime(fecha_reserva_str.split(' ')[0], '%Y-%m-%d').date()

            if nueva_fecha_fin < today:
                error_message = "La nueva fecha de finalización no puede ser una fecha pasada."
                return render_template('edit_reserva.html', detalles=detalles_reserva, error_message=error_message, reserva_id=reserva_id)

            if nueva_fecha_fin - fecha_reserva > timedelta(days=60):
                error_message = 'La fecha de finalización no puede exceder los 60 días desde la fecha de inicio.'
                return render_template('edit_reserva.html', detalles=detalles_reserva, error_message=error_message, reserva_id=reserva_id)

            library.update_reserva(reserva_id, nueva_fecha_fin_str)
            return redirect(url_for('mis_reservas'))

        except ValueError as e:
            error_message = f"Error al procesar la fecha: {e}"
            return render_template('edit_reserva.html', detalles=detalles_reserva, error_message=error_message, reserva_id=reserva_id)

    return render_template('edit_reserva.html', detalles=detalles_reserva, error_message=error_message, reserva_id=reserva_id)


@app.route('/reserve/return/<int:reserva_id>')
def return_reserva(reserva_id):
    library.return_reserva(reserva_id)
    return redirect(url_for('mis_reservas'))







@app.route('/review/rate/<int:book_id>', methods=['GET', 'POST'])
def rate_book(book_id):
    if request.method == 'POST':
        review_text = request.form['review']
        rating = request.form['rating']
        user_email = request.user.email

        library.add_or_update_review(user_email, book_id, review_text, rating)

        return redirect(url_for('mis_reservas'))

    # Para solicitudes GET, mostrar el formulario de reseña
    # Asegúrate de obtener cualquier dato necesario para mostrar en el formulario, como la reseña existente
    existing_review = library.get_reviews_by_book_id_and_user( request.user.email , book_id)  # Obtén la reseña existente si existe
    return render_template('review_form.html', book_id=book_id, review=existing_review)


###RED DE AMIGOS####

@app.route('/solicitudes',  methods=['GET', 'POST'])
def mostrar_solicitudes():
    user_email = request.user.email

    if not user_email:
        # Redirigir al usuario no autenticado a la página de inicio de sesión
        return redirect('/login')
    solicitudes = library.get_user_requests(user_email)
    if request.method == 'POST':
        email_solicitud = request.form['email_solicitud']
        if 'verPerfil' in request.form:
            return redirect(url_for('ver_perfil', user_email=request.form.get('email_solicitud')))
        if 'aceptarSol' in request.form:
            library.aceptar_solicitud(user_email,email_solicitud)
        elif 'rechazarSol' in request.form:
            library.rechazar_solicitud(user_email,email_solicitud)
    return render_template('solicitudes.html', solicitudes=solicitudes)

@app.route('/verUsuarios',  methods=['GET', 'POST'])
def mostrar_usuarios():
    emailSolicita = request.user.email
    usuarios = library.get_usuarios(emailSolicita)
    if request.method == 'POST':
        emailSolicitado = request.form.get('emailSolicitado')
        if not emailSolicitado == emailSolicita:
            library.enviar_solicitud(emailSolicita,emailSolicitado)
        if 'verPerfil' in request.form:
            return redirect(url_for('ver_perfil', user_email=request.form.get('emailSolicitado')))

    return render_template('verUsuarios.html', usuarios=usuarios)


@app.route('/amigos',  methods=['GET', 'POST'])
def mostrar_amigos():
    emailUser = request.user.email
    amigos = library.get_amigos(emailUser)
    if request.method == 'POST':
        if 'eliminar_amigo' in request.form:
            library.eliminar_amigo(emailUser,request.form.get('email_amigo'))
        if 'verPerfil' in request.form:
            return redirect(url_for('ver_perfil', user_email=request.form.get('email_amigo')))
    return render_template('amigos.html', amigos=amigos)

@app.route('/verPerfil', methods=['GET', 'POST'])
def ver_perfil():
    if request.args.get('header') == "1":
        emailUser = request.user.email
    else:
        emailUser = request.args.get('user_email')
    nombre = library.obtener_nombre(emailUser)
    amigos = library.get_amigos(emailUser)
    reservas_raw = library.get_user_reservas(emailUser)
    reservas = []
    resenas_raw = library.get_user_reviews(emailUser)
    resenas = []
    if request.method == 'POST':
        if 'verPerfil' in request.form:
            return redirect(url_for('ver_perfil', user_email=request.form.get('email_amigo')))
    for reserva in reservas_raw:
        libro_info = library.get_book_info(reserva['bookID'])
        if libro_info:
            reserva_modificada = {
                'id': reserva['id'],
                'bookID': libro_info.id,
                'titulo_libro': libro_info.title,  # Asegúrate de que estos campos existen en tu clase Book
                'nombre_autor': libro_info.author,
                'estado': reserva['estado'],
                'fecha_reserva': reserva['fecha_reserva'],
                'fecha_fin': reserva['fecha_fin']
            }
            reservas.append(reserva_modificada)
        else:
            error_message = "Error al cargar información de algunos libros."
    for resena in resenas_raw:
        libro_info = library.get_book_info(resena['libro_id'])
        if libro_info:
            resena_modificada = {
                'libro_id': resena['libro_id'],
                'bookID': libro_info.id,
                'titulo_libro': libro_info.title,  # Asegúrate de que estos campos existen en tu clase Book
                'nombre_autor': libro_info.author,
                'mensaje': resena['mensaje'],
                'puntuacion': resena['puntuacion'],
            }
            resenas.append(resena_modificada)

    return render_template('verPerfil.html', nombre=nombre,email=emailUser, amigos=amigos, reservas=reservas, resenas=resenas)