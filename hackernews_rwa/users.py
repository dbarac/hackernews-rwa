from flask import Blueprint, g, request
from flask.views import MethodView
from werkzeug.security import generate_password_hash
from hackernews_rwa.db import get_db

bp = Blueprint('users', __name__, url_prefix='/users')

class UserAPI(MethodView):

	def get(self, user_id):
		if user_id is None:
			pass
		else:
			#expose single user
			pass

	def post(self):
		#create new user
		request_data = request.get_json()
		username = request_data['username']
		password = request_data['password']
		#email is optional, set as None if not found in request data
		email = request_data.get('email', None)
		db = get_db()
		db_cursor = db.cursor()

		errors = {}
		if not username:
			errors['username'] = 'Username is required'
		elif db_cursor.execute(
			'SELECT id FROM user WHERE username = %s', (username,)
		) and db_cursor.fetchone() is not None:
			errors['username'] = 'User {} is already registered.'.format(username)
		if not password:
			errors['password'] = 'Password is required'

		if not errors:
			db_cursor.execute(
				'INSERT INTO user (username, password, email) VALUES (%s, %s, %s)',
				(username, generate_password_hash(password), email)
			)
			db.commit()
			return {
				"status": "success",
				"data": None
			}
		else:
			return {
				"status": "fail",
				"data": errors
			}

user_view = UserAPI.as_view('user_api')
bp.add_url_rule('/', view_func=user_view, methods=['POST'])

		

	
