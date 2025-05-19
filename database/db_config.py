import sqlite3

DATABASE_NAME = "stats_cinema_bot.db"

class Database:
	def __init__(self, db_name=DATABASE_NAME):
		self.db_name = db_name
		self.conn = None

	def create_connection(self):
		self.conn = sqlite3.connect(self.db_name)
		return self.conn
	
	

	def close_connection(self):
		if self.conn:
			self.conn.close()
			self.conn = None

