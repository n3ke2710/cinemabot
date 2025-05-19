import sqlite3
import os
from datetime import datetime

DATABASE_NAME = "stats_cinema_bot.db"

class Stats:
	def __init__(self, db_name=DATABASE_NAME):
		self.db_name = db_name
		self.conn = None

	def create_connection(self):
		self.conn = sqlite3.connect(self.db_name)
		return self.conn
	
	
	def create_tables(self):
		conn = self.create_connection()
		cursor = conn.cursor()
		cursor.execute("""
			CREATE TABLE IF NOT EXISTS users (
				id INTEGER PRIMARY KEY AUTOINCREMENT,
				username TEXT NOT NULL,
				telegram_id INTEGER UNIQUE NOT NULL,
				created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
			)
		""")
		cursor.execute("""
			CREATE TABLE IF NOT EXISTS service_stats (
				id INTEGER PRIMARY KEY AUTOINCREMENT,
				user_id INTEGER,
				action TEXT NOT NULL,
				timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
				FOREIGN KEY(user_id) REFERENCES users(id)
			)
		""")
		conn.commit()
		cursor.close()

	def create_user_history(self, user_id: int, action: str):
		# Insert action into service_stats table
		conn = self.create_connection()
		cursor = conn.cursor()
		cursor.execute(
			"INSERT INTO service_stats (user_id, action) VALUES (?, ?)",
			(user_id, action)
		)
		conn.commit()
		cursor.close()

		# Write action to log file in temp/{user_id}/
		log_dir = os.path.join("temp", str(user_id))
		os.makedirs(log_dir, exist_ok=True)
		log_file = os.path.join(log_dir, ".log")
		with open(log_file, "a", encoding="utf-8") as f:
			f.write(f"{datetime.now().isoformat()} - {action}\n")

	def close_connection(self):
		if self.conn:
			self.conn.close()
			self.conn = None

