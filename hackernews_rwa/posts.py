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
		db_cursor.execute(
			'SELECT * FROM post INNER JOIN on post.user_id = u.id'
			' (SELECT id, username FROM user) u WHERE id = %s', 
			(id,)
		)
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
		
		user_id = None
		if g.user:
			user_id = g.user['id']

		errors = {}
		db_cursor.execute(
			'SELECT * FROM post INNER JOIN'
			' (SELECT id, username FROM user) u ON post.user_id = u.id'
			' LEFT OUTER JOIN'
			' (select positive as user_vote_positive, user_id, post_id from post_vote'
			' where user_id = %s) v'
			' ON post.user_id = v.user_id AND post.id = v.post_id'
			+ ranking_sql[sort_by] + ' LIMIT %s OFFSET %s',
			(user_id, g.limit, g.offset)
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
				'SELECT * FROM comment INNER JOIN'
				' (SELECT id, username FROM user) u on comment.user_id = u.id'
				' WHERE post_id = %s ORDER BY depth, created',
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

	
	def create_comment_threads(self, comments_dq, prior_depth_comments = {}, depth = 0):
		"""
		Recursively build comment hierarchy from a dequeue of all comments.
		comments_dq is sorted by depth and timedate of creation.
		All child comments will be stored in a list as a property of the parent comment.
		The function is called recursively for each depth.
		"""
		if len(comments_dq) == 0:
			return
		#a collection of comments with current depth e.g. all root comments for depth 0 
		current_depth_comments = {} 
		
		while len(comments_dq) > 0 and comments_dq[0]['depth'] == depth:
			comment = comments_dq.popleft()
			comment['children'] = {}
			current_depth_comments[comment['id']] = comment
			if comment['parent_id'] in prior_depth_comments:
				prior_depth_comments[comment['parent_id']]['children'][comment['id']] = comment

		self.create_comment_threads(comments_dq, current_depth_comments, depth + 1)
		if depth == 0:
			structured_comments = current_depth_comments
			return self.comment_dicts_to_lists(structured_comments)
			

	def comment_dicts_to_lists(self, comments):
		for comment in comments.values():
			if comment['children']:
				comment['children'] = self.comment_dicts_to_lists(comment['children'])
		return list(comments.values())


	def post(self, post_id):
		if post_id: 
			if request.path.endswith('/comments'):
				return self.create_comment(post_id)
			elif request.path.endswith('/votes'):
				return self.create_vote(post_id) 
		else:
			return self.create_post()


	@login_required
	def create_comment(self, post_id):
		request_data = request.get_json()
		db = get_db()
		db_cursor = db.cursor()
		user_id = g.user['id']
		body = request_data.get('body')
		depth = 0

		errors = {}
		if not post_id:
			errors['post_id'] = 'Post is missing'
		if not body:
			errors['body'] = 'Content is missing.'

		#if parent_id is found in query params,
		#this comment will be a response to the comment with id = parent_id
		parent_id = request_data.get('parent_id')
		if parent_id:
			db_cursor.execute(
				'SELECT depth, post_id FROM comment WHERE id = %s', (parent_id,)
			)
			parent_comment = db_cursor.fetchone()
			if not parent_comment:
				errors['parent'] = 'Comment with id = parent_id does not exist'
			elif parent_comment['post_id'] != post_id:
				errors['parent'] = 'Parent comment is not related to selected post'
			else:
				depth = parent_comment['depth'] + 1

		if not errors:
			db_cursor.execute(
				'INSERT INTO comment (body, post_id, user_id, parent_id, depth)'
				' VALUES (%s, %s, %s, %s, %s)',
				(body, post_id, user_id, parent_id, depth)
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
	def create_vote(self, post_id):
		db = get_db()
		db_cursor = db.cursor()
		request_data = request.get_json()

		positive = True
		direction = request_data.get('direction', None)
		if direction and int(direction) == -1:
			positive = False

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
bp.add_url_rule('<int:post_id>/votes', view_func=post_view, methods=['POST', 'DELETE'])
