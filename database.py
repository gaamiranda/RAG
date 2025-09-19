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
		
	def store_document_in_db(self, metadata, chunks, embeddings):
		db = DatabaseConnection()
		
		#Check file hash

		query = "SELECT file_hash FROM documents;"
		db.cursor.execute(query)
		
		rows = db.cursor.fetchall()
		
		for row in rows:
			print(row)
			if row[0] == metadata["file_hash"]:
				print(f"❌ Error storing document: File_hash already exists")
				db.close()
				return None
		try:
			# Inserir documento e retornar o id
			insert_doc_query = """
				INSERT INTO documents (filename, file_path, total_pages, file_size, file_hash)
				VALUES (%s, %s, %s, %s, %s)
				RETURNING id;
			"""
			
			db.cursor.execute(insert_doc_query, (
				metadata['filename'],
				metadata['file_path'], 
				metadata['total_pages'],
				metadata['file_size'],
				metadata['file_hash']
			))
			
			document_id = db.cursor.fetchone()[0]
			
			insert_chunk_query = """
				INSERT INTO chunks (document_id, chunk_text, embedding, chunk_index)
				VALUES (%s, %s, %s, %s);
			"""
			
			for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
				
				embedding_list = embedding.tolist()
				
				db.cursor.execute(insert_chunk_query, (
					document_id,
					chunk,
					embedding_list,
					i
				))
			
			db.connection.commit()
			print(f"✅ Successfully stored document with ID: {document_id}")
			return document_id
			
		except Exception as e:
			print(f"❌ Error storing document: {e}")
			db.connection.rollback()
			return None
			
		finally:
			db.close()

	def close(self):
		if self.cursor:
			self.cursor.close()
		if self.connection:
			self.connection.close()
