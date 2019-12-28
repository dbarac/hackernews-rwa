import functools
from flask import request, g
from flaskext.mysql import MySQL 
import pymysql.cursors

db = MySQL(cursorclass = pymysql.cursors.DictCursor)
get_db = db.get_db

def paginate(view):
	@functools.wraps(view)
	def wrapped_view(*args, **kwargs):
		page_size = request.args.get('page_size')
		page = request.args.get('page')
		print(page_size)
		errors = {}
		if not page_size:
			page_size = 20
		if not page:
			page = 1 
		if not page_size.isnumeric() or not page.isnumeric():
			errors['pagination'] = 'page and page_size should be integers'
			return {
				"status": "fail",
				"errors": errors
			}
		page = int(page)
		page_size = int(page_size)
		g.limit = page_size
		#calculate offset for SQL query
		g.offset = (page - 1) * page_size
		return view(*args, **kwargs)
	
	return wrapped_view 