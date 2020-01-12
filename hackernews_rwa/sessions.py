import functools
from flask import Blueprint, g, request, session
from flask.views import MethodView
from werkzeug.security import generate_password_hash, check_password_hash
from hackernews_rwa.db import get_db

bp = Blueprint('sessions', __name__, url_prefix='/api/sessions')

class SessionAPI(MethodView):
	max_username_len = 64
	
	def get(self):
		return 'Hello'

	def post(self):
		#create session cookie and return it to the user
		request_data = request.get_json()
		#zamjenit sa request_data.get() jer mozda u req nema uname i pass
		username = request_data['username']
		password = request_data['password']
		db = get_db()
		db_cursor = db.cursor()

		errors = {}
		if not username:
			errors['username'] = 'Username is required'
		elif len(username) > self.max_username_len:
			errors['username'] = 'Username length is more than 64 characters'
		#check if password is correct only if there are no username format errors
		if not errors: 
			db_cursor.execute(
				'SELECT * FROM user WHERE username = %s', (username,)
			)
			user = db_cursor.fetchone()
			if user is None:
				errors['username'] = 'Incorrect username'
			if password is None:
				errors['password'] = 'Password required.'
			elif not check_password_hash(user['password'], password):
				errors['password'] = 'Incorrect password.'

		if not errors:
			session.clear()
			session['user_id'] = user['id']
			return {
				"status": "success",
				"data": None
			}
		else:
			return {
				"status": "fail",
				"data": errors
			}


	def delete(self):
		#logout user (delete the session cookie)
		session.clear()
		return {
			"status": "success",
			"data": None
		}


session_view = SessionAPI.as_view('session_api')
bp.add_url_rule('/', view_func=session_view, methods=['POST', 'DELETE', 'GET'])


#	*** session helper functions that will be used in other blueprints ***
		
#this function will be called at the beginning of each request
#(including requests from other blueprints)
@bp.before_app_request
def load_logged_in_user():
	user_id = session.get('user_id')

	if user_id is None:
		g.user = None
	else:
		db = get_db()
		db_cursor = db.cursor()
		db_cursor.execute(
			'SELECT * FROM user WHERE id = %s', (user_id,)
		)
		g.user = db_cursor.fetchone()	

#a decorator function which can be used to wrap functions for api endpoints
#that require a valid session cookie
def login_required(view):
	@functools.wraps(view)
	def wrapped_view(*args, **kwargs):
		if g.user is None:
			return {
				"status": "fail",
				"data": {
					"session": "login required"
				}
			}
		return view(*args, **kwargs)
	
	return wrapped_view 
