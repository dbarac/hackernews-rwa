import functools
from flask import request, g
from flaskext.mysql import MySQL 
import pymysql.cursors

db = MySQL(cursorclass = pymysql.cursors.DictCursor)
get_db = db.get_db

ranking_sql = {
	"top": "ORDER BY votes DESC",
	"rising": "ORDER BY votes / (1 + timestampdiff(hour, now(), created)) DESC",
	"new": "ORDER BY created DESC"
}

def paginate(view):
	@functools.wraps(view)
	def wrapped_view(*args, **kwargs):
		page_size = request.args.get('page_size')
		page = request.args.get('page')
		errors = {}
		if not page_size:
			page_size = 20
		if not page:
			page = 1
		if isinstance(page, str) and not page.isnumeric():
			errors['pagination'] = 'page query argument should be an integer'
		elif isinstance(page_size, str) and not page_size.isnumeric():
			errors['pagination'] = 'page_size should be an integer'
			return {
				"status": "fail",
				"errors": errors
			}

		page = int(page)
		page_size = int(page_size)
		#calculate limit and offset for SQL query
		#and save in g object until the end of the request
		g.limit = page_size
		g.offset = (page - 1) * page_size
		return view(*args, **kwargs)
	
	return wrapped_view 