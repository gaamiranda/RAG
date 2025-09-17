import os
import psycopg2

class DatabaseConnection:
	def __init__(self):
		self.connection = self._connect()
		self.cursor = self._get_cursor()

	def _connect(self):
		try:
			connection = psycopg2.connect(
				dbname=os.getenv("DB_NAME"),
				user=os.getenv("DB_USER"),
				password=os.getenv("DB_PASSWORD"),
				host=os.getenv("DB_HOST")
			)
			return connection
		except Exception as e:
			print(f"Error connecting to the database: {e}")
			return None

	def _get_cursor(self):
		if not self.connection:
			return None
		cursor = self.connection.cursor()
		return cursor if self._test_connection(cursor) else None

	def _test_connection(self, cursor):
		try:
			cursor.execute("SELECT version();")
			print(cursor.fetchone())
			return True
		except Exception as e:
			print(f"Error testing connection: {e}")
			return False
	def close(self):
		if self.cursor:
			self.cursor.close()
		if self.connection:
			self.connection.close()
