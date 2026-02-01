# RAG (Retrieval Augmented Generation) System

A local RAG system that allows you to upload PDF documents, store them with vector embeddings, and query them using natural language with AI-generated responses.

## Overview

This system implements a complete RAG pipeline:
1. **Document Ingestion** - Upload PDFs and extract text content
2. **Text Processing** - Chunk documents and generate vector embeddings
3. **Vector Storage** - Store embeddings in PostgreSQL with pgvector
4. **Semantic Search** - Find relevant chunks using vector similarity
5. **Answer Generation** - Generate responses using a local LLM (Ollama)

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              RAG PIPELINE                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  INGESTION PHASE:                                                           │
│  ┌──────────────┐    ┌─────────────────┐    ┌──────────────────┐           │
│  │   PDF File   │───>│ pdfprocessing.py│───>│ text_handling.py │           │
│  │              │    │ (Extract text + │    │ (Chunk text +    │           │
│  │              │    │  metadata)      │    │  generate embeds)│           │
│  └──────────────┘    └─────────────────┘    └────────┬─────────┘           │
│                                                       │                     │
│                                                       ▼                     │
│                                             ┌──────────────────┐            │
│                                             │   database.py    │            │
│                                             │ (PostgreSQL +    │            │
│                                             │  pgvector)       │            │
│                                             └────────┬─────────┘            │
│                                                      │                      │
│  QUERY PHASE:                                        ▼                      │
│  ┌──────────────┐    ┌─────────────────┐    ┌──────────────────┐           │
│  │ User Query   │───>│   ingest.py     │───>│    Ollama        │           │
│  │              │    │ (Embed query +  │    │ (llama2 model)   │           │
│  │              │    │  vector search) │    │ Generate answer  │           │
│  └──────────────┘    └─────────────────┘    └──────────────────┘           │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Project Structure

| File | Description |
|------|-------------|
| `frontend.py` | Main entry point - Flet-based web UI for uploading PDFs and querying |
| `setup.py` | CLI-based document ingestion alternative |
| `pdfprocessing.py` | Extracts text and metadata from PDF files using pdfplumber |
| `text_handling.py` | Chunks text into segments and generates embeddings using SentenceTransformers |
| `database.py` | PostgreSQL database operations (stores documents and vector embeddings) |
| `ingest.py` | Query processing - embeds queries, performs vector search, generates answers |
| `pyproject.toml` | Project configuration and dependencies |

## Requirements

- Python >= 3.13
- PostgreSQL with [pgvector](https://github.com/pgvector/pgvector) extension
- [Ollama](https://ollama.ai/) running locally with the `llama2` model

## Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd RAG
```

### 2. Install Python dependencies

Using uv (recommended):
```bash
uv sync
```

Or using pip:
```bash
pip install psycopg2-binary python-dotenv pdfplumber sentence-transformers ollama flet
```

### 3. Set up PostgreSQL with pgvector

First, install the pgvector extension in your PostgreSQL database:

```sql
CREATE EXTENSION vector;
```

Then create the required tables:

```sql
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255),
    file_path TEXT,
    total_pages INTEGER,
    file_size BIGINT,
    file_hash VARCHAR(32) UNIQUE
);

CREATE TABLE chunks (
    id SERIAL PRIMARY KEY,
    document_id INTEGER REFERENCES documents(id),
    chunk_text TEXT,
    embedding vector(384),  -- MiniLM-L6-v2 produces 384-dimensional vectors
    chunk_index INTEGER
);
```

### 4. Install and configure Ollama

Install Ollama from [ollama.ai](https://ollama.ai/), then pull the llama2 model:

```bash
ollama pull llama2
ollama serve
```

### 5. Configure environment variables

Create a `.env` file in the project root:

```env
DB_NAME=your_database_name
DB_USER=your_database_user
DB_PASSWORD=your_database_password
DB_HOST=your_database_host
```

## Usage

### Web Interface (Recommended)

Launch the Flet web application:

```bash
python frontend.py
```

This opens a browser interface where you can:
1. Upload PDF documents
2. Ask questions about your uploaded documents
3. Receive AI-generated answers based on relevant content

### CLI Ingestion

For batch processing documents via command line:

```bash
python setup.py
```

Note: You may need to modify the file path in `setup.py` for your specific use case.

## Configuration

The system uses the following default settings (configurable in the source files):

| Setting | Value | Location |
|---------|-------|----------|
| Chunk size | 600 characters | `text_handling.py` |
| Chunk overlap | 75 characters | `text_handling.py` |
| Embedding model | `all-MiniLM-L6-v2` | `text_handling.py` |
| LLM model | `llama2` | `ingest.py` |
| Top-K results | 5 chunks | `ingest.py` |

## How It Works

### Document Ingestion

1. **PDF Upload**: User uploads a PDF file through the web interface
2. **Text Extraction**: `pdfprocessing.py` uses pdfplumber to extract text and metadata (page count, file size)
3. **Deduplication**: MD5 hash prevents re-ingesting duplicate documents
4. **Chunking**: `text_handling.py` splits text into overlapping chunks of ~600 characters
5. **Embedding**: Each chunk is embedded using the `all-MiniLM-L6-v2` model (384 dimensions)
6. **Storage**: Documents and chunks with embeddings are stored in PostgreSQL

### Query Processing

1. **Query Embedding**: User's question is embedded using the same model
2. **Vector Search**: pgvector finds the 5 most similar chunks using cosine distance
3. **Context Building**: Retrieved chunks are combined as context
4. **Answer Generation**: Ollama's llama2 model generates an answer based on the context

## Testing the Pipeline

1. Start Ollama: `ollama serve`
2. Launch the app: `python frontend.py`
3. Upload a PDF document through the web interface
4. Wait for processing to complete
5. Ask a question about the document content
6. Receive an AI-generated answer based on relevant passages

## Troubleshooting

### Database connection issues
- Verify PostgreSQL is running
- Check `.env` file credentials
- Ensure pgvector extension is installed

### Ollama not responding
- Verify Ollama is running: `ollama serve`
- Check the llama2 model is installed: `ollama list`

### Slow embedding generation
- First run downloads the embedding model (~90MB)
- Subsequent runs will be faster

