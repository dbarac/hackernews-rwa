from flask import Blueprint, g, request
from flask.views import MethodView
from hackernews_rwa.db import get_db
from hackernews_rwa.sessions import login_required

bp = Blueprint('comments', __name__, url_prefix='/api/comments')

class CommentAPI(MethodView):

	def get(self, id):
		db = get_db()
		db_cursor = db.cursor()

		errors = {}
		db_cursor.execute('SELECT * FROM comment WHERE id = %s', (id,))
		comment = db_cursor.fetchone()
		if comment is None:
			errors['comment_id'] = 'Comment not found.'

		if not errors:
			return {
				"status": "success",
				"data": comment
			}
		else:
			return {
				"status": "fail",
				"data": errors
			}


	def post(self, id):
		if request.path.endswith('/votes'):
			return self.create_vote(id) 


	@login_required
	def create_vote(self, comment_id):
		db = get_db()
		db_cursor = db.cursor()
		request_data = request.get_json()

		positive = True
		direction = request_data.get('direction', None)
		if direction and int(direction) == -1:
			positive = False

		errors = {}
		db_cursor.execute(
			'SELECT * FROM comment_vote WHERE user_id = %s AND comment_id = %s',
			(g.user['id'], comment_id)
		)
		vote = db_cursor.fetchone()
		if vote:
			if positive and vote['positive']:
				errors['vote'] = 'Positive vote already exists.'
			elif not positive and not vote['positive']:
				errors['vote'] = 'Negative vote already exists.'

		if not errors:
			if vote:
				db_cursor.execute(
					'UPDATE comment_vote SET positive = %s' 
					' WHERE user_id = %s and comment_id = %s',
					(positive, g.user['id'], comment_id)
				)
			else:
				db_cursor.execute(
					'INSERT INTO comment_vote (user_id, comment_id, positive)'
					' VALUES (%s, %s, %s)', (g.user['id'], comment_id, positive)
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


	def delete(self, id):
		if request.path.endswith('/votes'):
			return self.delete_vote(id) 
		else:
			return self.delete_comment(id)


	@login_required
	def delete_vote(self, comment_id):
		db = get_db()
		db_cursor = db.cursor()

		errors = {}
		db_cursor.execute(
			'SELECT * FROM comment_vote WHERE user_id = %s AND comment_id = %s',
			(g.user['id'], comment_id)
		)
		vote = db_cursor.fetchone()
		if not vote:
			errors['vote'] = 'Vote does not exist.'

		if not errors:
			db_cursor.execute(
				'DELETE FROM comment_vote WHERE user_id = %s and comment_id = %s',
				(g.user['id'], comment_id)
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
	def delete_comment(self, id):
		db = get_db()
		db_cursor = db.cursor()
		#provjerit foreign key constraint u bazi kad se brise user (postovi, komentari)	

		errors = {}
		db_cursor.execute('SELECT * FROM comment WHERE id = %s', (id, ))
		comment = db_cursor.fetchone()
		if not comment:
			errors['id'] = 'Comment with selected id does not exist'
		elif int(comment['user_id']) != g.user['id']:
			errors['id'] = 'user does not own selected post'

		if not errors:
			#provjerit ako je delete uspio
			db_cursor.execute('DELETE FROM comment WHERE id = %s', (id,))
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
	def patch(self, id):
		request_data = request.get_json()
		db = get_db()
		db_cursor = db.cursor()
		#provjerit foreign key constraint u bazi kad se brise user (postovi, komentari)	

		errors = {}
		db_cursor.execute('SELECT * FROM comment WHERE id = %s', (id, ))
		comment = db_cursor.fetchone()
		if not comment:
			errors['id'] = 'Comment with selected id does not exist'
		elif int(comment['user_id']) != g.user['id']:
			errors['id'] = 'user does not own selected post'
		else:
			body = request_data.get('body', None)
			if not body:
				errors['body'] = 'No content was found in update request'

		if not errors:
			db_cursor.execute(
				'UPDATE comment SET body = %s, edited = 1 WHERE id = %s', (body, id)
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

comment_view = CommentAPI.as_view('comment_api')
bp.add_url_rule('/<int:id>', view_func=comment_view, methods=['GET', 'DELETE', 'PATCH'])
bp.add_url_rule('<int:id>/votes', view_func=comment_view, methods=['POST', 'DELETE'])