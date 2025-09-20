from sentence_transformers import SentenceTransformer
from database import DatabaseConnection
from dotenv import load_dotenv
import ollama

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
		
		return results
		
	except Exception as e:
		print(f"❌ Error searching chunks: {e}")
		return None
	finally:
		db.close()

def generate_answer(similar_chunks, question):
    conversation = [
        {
            "role": "system", 
            "content": """You are a helpful assistant that answers questions based on provided context. 
						Use the context chunks to answer the user's question. 
						If the chunks don't contain relevant information, say so.
						Always mention which parts of your answer come from the provided context.
						Also, not every chunk needs to be used, sometimes chunks may not make sense"""
        },
        {
            "role": "user", 
            "content": f"""Question: {question}

							Context chunks:
							{similar_chunks}
							
							Please answer the question based on the context provided."""
        }
    ]
    
    print("🤖 Calling Ollama, this may take a while...")
    reply = ollama.chat(model='llama2', messages=conversation)
    return reply['message']['content']

if __name__ == "__main__":
	question = input("What do you want to search for? ")
	embedding = process_query(question)
	similar_chunks = search_similar_chunks(embedding)
	final_answer = generate_answer(similar_chunks, question)
	print(final_answer)