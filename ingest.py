from sentence_transformers import SentenceTransformer
from database import DatabaseConnection
from dotenv import load_dotenv

load_dotenv()
TEXT_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

def process_query(text):
	model = SentenceTransformer(TEXT_MODEL_NAME)
	embeddings = model.encode(text)
	return embeddings.tolist()


def search_similar_chunks(query_embedding, top_k=5):
	db = DatabaseConnection()
	
	if not db.connection or not db.cursor:
		print("❌ Failed to connect to database")
		return None
	
	try:
		query = """
			SELECT chunk_text, embedding <=> %s::vector as distance 
			FROM chunks 
			ORDER BY embedding <=> %s::vector 
			LIMIT %s
		"""
		
		db.cursor.execute(query, (query_embedding, query_embedding, top_k))
		results = db.cursor.fetchall()
		
		print(results)
		return results
		
	except Exception as e:
		print(f"❌ Error searching chunks: {e}")
		return None
	finally:
		db.close()


if __name__ == "__main__":
	embedding = process_query(input("What do you want to search for?"))
	search_similar_chunks(embedding)