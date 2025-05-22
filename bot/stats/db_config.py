import sqlite3
import os
import logging
from datetime import datetime
from typing import List, Tuple, Optional

logger = logging.getLogger(__name__)

DATABASE_NAME = "stats_cinema_bot.db"

class Stats:
	def __init__(self, db_name: str = DATABASE_NAME):
		self.db_name = db_name
		try:
			self.conn = sqlite3.connect(
				self.db_name,
				check_same_thread=False,
				timeout=30
			)
			self._create_tables()
		except sqlite3.Error as e:
			logger.error(f"Ошибка при подключении к базе данных: {e}")
			raise

	def _create_tables(self) -> None:
		try:
			with self.conn:
				self.conn.execute("""
					CREATE TABLE IF NOT EXISTS users (
						id INTEGER PRIMARY KEY AUTOINCREMENT,
						username TEXT NOT NULL,
						telegram_id INTEGER UNIQUE NOT NULL,
						created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
					)
				""")
				self.conn.execute("""
					CREATE TABLE IF NOT EXISTS service_stats (
						id INTEGER PRIMARY KEY AUTOINCREMENT,
						user_id INTEGER,
						action TEXT NOT NULL,
						timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
						FOREIGN KEY(user_id) REFERENCES users(id)
					)
				""")
				self.conn.execute("""
					CREATE TABLE IF NOT EXISTS request_history (
						id INTEGER PRIMARY KEY AUTOINCREMENT,
						user_id INTEGER NOT NULL,
						query TEXT NOT NULL,
						timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
					)
				""")
				self.conn.execute("""
					CREATE TABLE IF NOT EXISTS query_stats (
						query TEXT PRIMARY KEY,
						count INTEGER DEFAULT 0
					)
				""")
				self.conn.execute("""
					CREATE TABLE IF NOT EXISTS liked_movies (
						id INTEGER PRIMARY KEY AUTOINCREMENT,
						user_id INTEGER,
						movie_title TEXT NOT NULL
					)
				""")
		except sqlite3.Error as e:
			logger.error(f"Ошибка при создании таблиц: {e}")
			raise

	def save_request(self, user_id: int, query: str) -> None:
		try:
			with self.conn:
				self.conn.execute(
					"INSERT INTO request_history (user_id, query) VALUES (?, ?)",
					(user_id, query)
				)
				self.conn.execute("""
					INSERT INTO query_stats (query, count)
					VALUES (?, 1)
					ON CONFLICT(query) DO UPDATE SET count = count + 1
				""", (query,))
		except sqlite3.Error as e:
			logger.error(f"Ошибка при сохранении запроса: {e}")
			raise

	def get_request_history(
		self,
		user_id: int,
		limit: int = 10
	) -> List[Tuple[str, str]]:
		try:
			cursor = self.conn.cursor()
			cursor.execute(
				"""
				SELECT query, timestamp 
				FROM request_history 
				WHERE user_id = ? 
				ORDER BY timestamp DESC 
				LIMIT ?
				""",
				(user_id, limit)
			)
			results = cursor.fetchall()
			cursor.close()
			return results
		except sqlite3.Error as e:
			logger.error(f"Ошибка при получении истории запросов: {e}")
			return []

	def create_user_history(self, user_id: int, action: str) -> None:
		try:
			with self.conn:
				self.conn.execute(
					"INSERT INTO service_stats (user_id, action) VALUES (?, ?)",
					(user_id, action)
				)
			log_dir = os.path.join("temp", str(user_id))
			os.makedirs(log_dir, exist_ok=True)
			log_file = os.path.join(log_dir, ".log")
			with open(log_file, "a", encoding="utf-8") as f:
				f.write(f"{datetime.now().isoformat()} - {action}\n")
		except (sqlite3.Error, IOError) as e:
			logger.error(f"Ошибка при создании истории пользователя: {e}")
			raise

	def save_liked_movie(self, user_id: int, movie_title: str) -> None:
		try:
			with self.conn:
				self.conn.execute(
					"INSERT INTO liked_movies (user_id, movie_title) VALUES (?, ?)",
					(user_id, movie_title)
				)
		except sqlite3.Error as e:
			logger.error(f"Ошибка при сохранении понравившегося фильма: {e}")
			raise

	def watch_liked_movies(self, user_id: int) -> List[str]:
		try:
			cursor = self.conn.cursor()
			cursor.execute(
				"SELECT movie_title FROM liked_movies WHERE user_id = ?",
				(user_id,)
			)
			movies = cursor.fetchall()
			cursor.close()
			return [movie[0] for movie in movies]
		except sqlite3.Error as e:
			logger.error(f"Ошибка при получении понравившихся фильмов: {e}")
			return []

	def get_top_queries(self, limit: int = 10) -> List[Tuple[str, int]]:
		try:
			cursor = self.conn.cursor()
			cursor.execute("""
				SELECT query, count FROM query_stats
				ORDER BY count DESC
				LIMIT ?
			""", (limit,))
			results = cursor.fetchall()
			cursor.close()
			return results
		except sqlite3.Error as e:
			logger.error(f"Ошибка при получении топ запросов: {e}")
			return []

	def close_connection(self) -> None:
		try:
			if self.conn:
				self.conn.close()
				self.conn = None
		except sqlite3.Error as e:
			logger.error(f"Ошибка при закрытии соединения с базой данных: {e}")
			raise

	def __del__(self) -> None:
		self.close_connection()
