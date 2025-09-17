import pdfplumber
import os
from datetime import datetime
import hashlib

def pdf_data_extraction(path):
	metadata = {}
	content = ""
	with pdfplumber.open(path) as pdf:
		pages = pdf.pages
		for page in pages:
			text = page.extract_text()
			if text:
				content += text + "\n"
	metadata["filename"] = path.split("/")[-1]
	metadata["file_path"] = path
	metadata["total_pages"] = len(pages)
	metadata["file_size"] = os.path.getsize(path)
	metadata["processing_date"] = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
	metadata["file_hash"] = hashlib.md5(content.encode()).hexdigest()
	metadata["content"] = content
	return metadata

