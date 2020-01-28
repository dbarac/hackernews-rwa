import os
from flask import Flask

def create_app(test_config=None):
	#create and configure the app
	app = Flask(__name__, instance_relative_config=True)
	app.config.from_mapping(
		SECRET_KEY='dev',
		MYSQL_DATABASE_USER='hackernews',
		MYSQL_DATABASE_PASSWORD='hackernews',
		MYSQL_DATABASE_DB='hackernews',
	)

	if test_config is None:
		#load the instance config, if it exists, when not testing
		app.config.from_pyfile('config.py', silent=True)
	else:
		#load the test config if passed in 
		app.config.from_mapping(test_config)

	#ensure the instance folder exists
	try:
		os.makedirs(app.instance_path)
	except OSError:
		pass
	
	#setup database and api blueprints
	from .db import db
	db.init_app(app)

	from . import users
	app.register_blueprint(users.bp)

	from . import sessions
	app.register_blueprint(sessions.bp)

	from . import posts
	app.register_blueprint(posts.bp)

	from . import comments
	app.register_blueprint(comments.bp)

	#a simple page that says hello
	@app.route('/hello')
	def hello():
		return 'Hello, World'


	@app.route('/hello2')
	def hello2():
		cursor = db.get_db().cursor()	
		with app.open_resource('schema.sql') as f:
			cursor.executemany(f.read().decode('utf8'), ())
		return {
			"hello": "Hello, World"
		}

	return app
