from flaskext.mysql import MySQL 
import pymysql.cursors

db = MySQL(cursorclass = pymysql.cursors.DictCursor)
get_db = db.get_db

