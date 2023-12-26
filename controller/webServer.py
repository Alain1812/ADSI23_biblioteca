from .LibraryController import LibraryController
from flask import Flask, render_template, request, make_response, redirect

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


@app.route('/reserve', methods=['POST'])

@app.route('/reserve', methods=['POST'])
def reserve_book():
    user_id = request.cookies.get('user_id')  # Assuming user ID is stored in cookies
    book_id = request.form['copy_id']
    start_date = request.form['start_date']  # Assuming start date is provided in the form
    end_date = request.form['end_date']  # Assuming end date is provided in the form
    if library.create_reservation(user_id, book_id, start_date, end_date):
        return redirect('/reservations')
    else:
        return 'Reservation failed', 400

    # Esto incluiría obtener los datos de la solicitud, como el ID del usuario y el ID del libro,
    # y llamar al método de crear reserva en el controlador
    pass

@app.route('/reservations')
def reservations():
    if 'user' in dir(request) and request.user and request.user.token:
        # Here, implement logic to fetch and display user's reservation history
        # This could involve calling a method from the controller and passing data to an HTML template
        return render_template('reservations.html')  # Replace with actual reservations template
    else:
        # User is not logged in, show a warning message
        return render_template('login_warning.html')  # Replace with a template showing login warning

def user_reservations():
    # Aquí iría la lógica para mostrar el historial de reservas de un usuario
    # Esto incluiría llamar al método correspondiente en el controlador y
    # pasar los datos a una plantilla HTML para su visualización
    pass
