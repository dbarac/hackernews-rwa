from collections import deque
from flask import Blueprint, g, request
from flask.views import MethodView
from hackernews_rwa.db import get_db, paginate, ranking_sql
from hackernews_rwa.sessions import login_required


bp = Blueprint('posts', __name__, url_prefix='/api/posts')

class PostAPI(MethodView):

	def get(self, post_id):
		if post_id is None:
			return self.get_posts()
		else:
			if request.path.endswith('/comments'):
				return self.get_post_comments(post_id)
			else:
				#expose single post
				return self.get_post(post_id)


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


	@paginate
	def get_posts(self):
		db = get_db()
		db_cursor = db.cursor()

		sort_by = request.args.get('sort_by')
		if sort_by not in ('top', 'rising', 'new'):
			sort_by = 'rising'
		
		errors = {}
		db_cursor.execute(
			'SELECT * FROM post ' + ranking_sql[sort_by] + ' LIMIT %s OFFSET %s',
			(g.limit, g.offset)
			)
		posts = db_cursor.fetchall()
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

	
	def get_post_comments(self, post_id):
		db = get_db()
		db_cursor = db.cursor()

		errors = {}
		db_cursor.execute('SELECT * FROM post WHERE id = %s', (post_id,))
		post = db_cursor.fetchone()
		if not post:
			errors['post_id'] = 'Post with given id does not exist'

		if not errors:
			db_cursor.execute(
				'SELECT * FROM comment WHERE post_id = %s',
				(post_id,)
			)
			comments = db_cursor.fetchall()
			#comments = create_comment_threads(deque(comments))
			return {
				"status": "success",
				"data": comments
			}
		else:
			return {
				"status": "fail",
				"data": errors
			}

	
	def create_comment_threads(comments, prior_depth = {}):
		"""
		Recursively build comment hierarchy from a queue of all comments.
		All child comments will be stored in a list as a property of the parent comment.
		"""

		comments = deque(comments)
		structured_comments = {}
		#a collection of comments with current depth e.g. all root comments for depth 0 
		current_depth = {} 
		
		for comment in comments:
			if comment['parent'] == None or comment['parent_id'] in current_depth:
				structured_comments[comment['id']] = comment


	def post(self, post_id):
		if post_id: 
			if request.path.endswith('/comments'):
				return self.create_comment(post_id)
			elif request.path.endswith('/upvotes'):
				return self.create_vote(post_id, positive=True) 
			elif request.path.endswith('/downvotes'):
				return self.create_vote(post_id, positive=False)
		else:
			return create_post(self)


	@login_required
	def create_comment(self, post_id):
		request_data = request.get_json()
		db = get_db()
		db_cursor = db.cursor()
		user_id = g.user['id']
		body = request_data.get('body')

		#if parent_id is found in query params,
		#this comment will be a response to the comment with id = parent_id
		parent_id = request.args.get('parent_id')
		
		errors = {}
		if not post_id:
			errors['post_id'] = 'Post is missing'
		if not body:
			errors['body'] = 'Content is missing.'

		if not errors:
			db_cursor.execute(
				'INSERT INTO comment (body, post_id, user_id, parent_id)'
				' VALUES (%s, %s, %s, %s)',
				(body, post_id, user_id, parent_id)
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
	def create_post(self):
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
	def create_vote(self, post_id, positive):
		db = get_db()
		db_cursor = db.cursor()

		errors = {}
		db_cursor.execute(
			'SELECT * FROM post_vote WHERE user_id = %s AND post_id = %s',
			(g.user['id'], post_id)
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
					'UPDATE post_vote SET positive = %s' 
					' WHERE user_id = %s and post_id = %s',
					(positive, g.user['id'], post_id)
				)
			else:
				db_cursor.execute(
					'INSERT INTO post_vote (user_id, post_id, positive)'
					' VALUES (%s, %s, %s)', (g.user['id'], post_id, positive)
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


	def delete(self, post_id):
		if request.path.endswith('/upvotes'):
			return self.delete_vote(post_id) 
		elif request.path.endswith('/downvotes'):
			return self.delete_vote(post_id)
		else:
			return self.delete_post(post_id)


	@login_required
	def delete_vote(self, post_id):
		db = get_db()
		db_cursor = db.cursor()

		errors = {}
		db_cursor.execute(
			'SELECT * FROM post_vote WHERE user_id = %s AND post_id = %s',
			(g.user['id'], post_id)
		)
		vote = db_cursor.fetchone()
		if not vote:
			errors['vote'] = 'Vote does not exist.'

		if not errors:
			db_cursor.execute(
				'DELETE FROM post_vote WHERE user_id = %s and post_id = %s',
				(g.user['id'], post_id)
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
	def delete_post(self, id):
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


	@login_required
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
bp.add_url_rule('/', view_func=post_view, defaults={'post_id': None}, methods=['GET', 'POST'])
bp.add_url_rule('/<int:post_id>', view_func=post_view, methods=['GET', 'DELETE', 'PATCH'])
bp.add_url_rule('/<int:post_id>/comments', view_func=post_view, methods=['GET', 'POST'])
bp.add_url_rule('<int:post_id>/upvotes', view_func=post_view, methods=['POST', 'DELETE'])
bp.add_url_rule('<int:post_id>/downvotes', view_func=post_view, methods=['POST', 'DELETE'])
