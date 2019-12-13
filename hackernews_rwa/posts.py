from flask import Blueprint, g, request
from flask.views import MethodView
from hackernews_rwa.db import get_db
from hackernews_rwa.sessions import login_required

bp = Blueprint('posts', __name__, url_prefix='/posts')

class PostAPI(MethodView):

	def get(self, id):
		if id is None:
			return self.get_posts()
		else:
			#expose single post
			return self.get_post(id)


	def get_post(self, id):
		db = get_db()
		db_cursor = db.cursor()

		errors = {}
		db_cursor.execute('SELECT * FROM post WHERE id = %s', (id,))
		post = db_cursor.fetchone()
		if post is None:
			errors['post_id'] = 'Post not found.'

		if not errors:
			return {
				"status": "success",
				"data": post
			}
		else:
			return {
				"status": "fail",
				"data": errors
			}


	def get_posts(self):
		db = get_db()
		db_cursor = db.cursor()

		errors = {}
		db_cursor.execute('SELECT * FROM post')
		posts = db_cursor.fetchall()
		#posts = [post for post in posts]
		if not errors:
			return {
				"status": "success",
				"data": posts
			}
		else:
			return {
				"status": "fail",
				"data": errors
			}


	@login_required
	def post(self):
		#create new post
		request_data = request.get_json()
		title = request_data.get('title', None)
		url = request_data.get('url', None)
		body = request_data.get('body', None)
		db = get_db()
		db_cursor = db.cursor()

		errors = {}
		if not title:
			errors['title'] = 'Title is required'

		if not errors:
			db_cursor.execute(
				'INSERT INTO post (title, url, body, user_id) VALUES (%s, %s, %s, %s)',
				(title, url, body, g.user['id'])
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
		db_cursor.execute('SELECT * FROM post WHERE id = %s', (id, ))
		post = db_cursor.fetchone()
		if not post:
			errors['id'] = 'post with selected id does not exist'
		elif int(post['user_id']) != g.user['id']:
			errors['id'] = 'user does not own selected post'

		if not errors:
			#provjerit ako je delete uspio
			db_cursor.execute('DELETE FROM post WHERE id = %s', (id,))
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


	def patch(self, id):
		request_data = request.get_json()
		db = get_db()
		db_cursor = db.cursor()
		#provjerit foreign key constraint u bazi kad se brise user (postovi, komentari)	

		errors = {}
		db_cursor.execute('SELECT * FROM post WHERE id = %s', (id, ))
		post = db_cursor.fetchone()
		if not post:
			errors['id'] = 'post with selected id does not exist'
		elif int(post['user_id']) != g.user['id']:
			errors['id'] = 'user does not own selected post'
		else:
			body = request_data.get('body', None)
			if not body:
				errors['body'] = 'No content was found in update request'

		if not errors:
			db_cursor.execute(
				'UPDATE post SET body = %s, edited = 1 WHERE id = %s', (body, id)
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




post_view = PostAPI.as_view('post_api')
bp.add_url_rule('/', view_func=post_view, defaults={'id': None}, methods=['GET', 'POST'])
bp.add_url_rule('/<int:id>', view_func=post_view, methods=['GET', 'DELETE', 'PATCH'])
