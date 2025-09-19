from database import DatabaseConnection
from dotenv import load_dotenv
from pdfprocessing import pdf_data_extraction
from sentence_transformers import SentenceTransformer

load_dotenv()

def chunk_text(text, chunk_size=600, overlap=75):
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size

        # último chunk
        if end >= len(text):
            chunks.append(text[start:])
            break
        
        # break point
        break_point = end
        for i in range(end - 1, start, -1):
            if i < len(text) and text[i] in [".", "!", "?", "\n"]:
                break_point = i + 1
                break
        
        chunks.append(text[start:break_point])
        
        start = break_point - overlap
        if start < 0:
            start = 0
    
    return chunks


if __name__ == "__main__":
    file = ""
    #db = DatabaseConnection()
    #db.close()
    data = pdf_data_extraction(file)
    chunk_text(data["content"])
    