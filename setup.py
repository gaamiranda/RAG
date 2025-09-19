from database import DatabaseConnection
from dotenv import load_dotenv
from pdfprocessing import pdf_data_extraction
from text_handling import *
load_dotenv()


if __name__ == "__main__":
    file = "/Users/goncalomiranda/Desktop/42/cpp/cpp00/cpp00.pdf"
    metadata = pdf_data_extraction(file)
    chunks = chunk_text(metadata["content"])
    embeddings = chunks_embedding(chunks)
    DatabaseConnection().store_document_in_db(metadata, chunks, embeddings)