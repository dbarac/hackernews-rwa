from flask import Blueprint, g, request
from flask.views import MethodView
from werkzeug.security import generate_password_hash
from hackernews_rwa.db import get_db
from hackernews_rwa.sessions import login_required

bp = Blueprint('users', __name__, url_prefix='/api/users')

class UserAPI(MethodView):
	max_username_len = 64
	max_about_len = 512

	def get(self, user_id):
		if user_id is None:
			pass
		else:
			if request.path.endswith('/posts'):
				return self.get_posts_by_user(user_id)		
			elif request.path.endswith('/comments'):
				return self.get_comments_by_user(user_id)
			elif request.path.endswith('/scores'):
				return self.get_user_scores(user_id)
	

	def get_posts_by_user(self, user_id):
		db = get_db()
		db_cursor = db.cursor()

		errors = {}
		db_cursor.execute('SELECT * FROM user WHERE id = %s', (user_id))
		user = db_cursor.fetchone()
		if not user:
			errors['user_id'] = 'User with given id does not exist'

		if not errors:
			db_cursor.execute('SELECT * FROM post WHERE user_id = %s', (user_id))
			posts = db_cursor.fetchall()
			return {
				"status": "success",
				"data": posts
			}
		else:
			return {
				"status": "fail",
				"data": errors
			}


	def get_comments_by_user(self, user_id):
		db = get_db()
		db_cursor = db.cursor()

		errors = {}
		db_cursor.execute('SELECT * FROM user WHERE id = %s', (user_id))
		user = db_cursor.fetchone()
		if not user:
			errors['user_id'] = 'User with given id does not exist'

		if not errors:
			db_cursor.execute('SELECT * FROM comment WHERE user_id = %s', (user_id))
			comments = db_cursor.fetchall()
			return {
				"status": "success",
				"data": comments
			}
		else:
			return {
				"status": "fail",
				"data": errors
			}


	def get_user_scores(self, user_id):
		db = get_db()
		db_cursor = db.cursor()

		errors = {}
		db_cursor.execute('SELECT * FROM user WHERE id = %s', (user_id))
		user = db_cursor.fetchone()
		if not user:
			errors['user_id'] = 'User with given id does not exist'

		if not errors:
			db_cursor.execute(
			'SELECT SUM(votes) as score FROM post WHERE user_id = %s', (user_id)
			)
			posts_score = db_cursor.fetchone()['score']
			if not posts_score:
				posts_score = 0
			db_cursor.execute(
				'SELECT SUM(votes) as score FROM comment WHERE user_id = %s', (user_id)
			)
			comment_score = db_cursor.fetchone()['score']
			if not comment_score:
				comment_score = 0

			scores = {
				"posts_score": int(posts_score),
				"comment_score": int(comment_score)
			}
			return {
				"status": "success",
				"data": scores
			}
		else:
			return {
				"status": "fail",
				"data": errors
			}



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
		elif len(username) > self.max_username_len:
			errors['username'] = 'Username length is more than 64 characters'
		elif db_cursor.execute(
			'SELECT id FROM user WHERE username = %s', (username,)
		) and db_cursor.fetchone() is not None:
			errors['username'] = 'User {} is already registered.'.format(username)
		if not password:
			errors['password'] = 'Password is required'
		if email is not None:
			if len(email) > 0:
				db_cursor.execute(
					'SELECT email FROM user WHERE email = %s', (email,)
				)
				if db_cursor.fetchone():
					errors['email'] = 'email is already used by another user'
			else:
				email = None #set to null in db

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


	@login_required
	def delete(self, id):
		db = get_db()
		db_cursor = db.cursor()
		#provjerit foreign key constraint u bazi kad se brise user (postovi, komentari)	
		errors = {}
		if int(g.user['id']) != id:
			errors['id'] = 'user id does not match login id'
		else:
			#provjerit ako je delete uspio
			db_cursor.execute('DELETE FROM user WHERE id = %s', (id,))
			db.commit()

		if not errors:
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
bp.add_url_rule('/<int:user_id>', view_func=user_view, methods=['GET', 'DELETE'])
bp.add_url_rule('/<int:user_id>/posts', view_func=user_view, methods=['GET'])
bp.add_url_rule('/<int:user_id>/comments', view_func=user_view, methods=['GET'])
bp.add_url_rule('/<int:user_id>/scores', view_func=user_view, methods=['GET'])
