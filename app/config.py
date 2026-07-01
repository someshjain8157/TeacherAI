from pathlib import Path

# Project folders
PROJECT_ROOT = Path(__file__).resolve().parent.parent
BOOKS_DIR = PROJECT_ROOT / "books"
CHROMA_DIR = PROJECT_ROOT / "chromadb"

# Ollama model
OLLAMA_MODEL = "phi3:mini"
# OLLAMA_MODEL = "llama3.1:8b"
# OLLAMA_MODEL = "mistral:7b"

# Embedding model
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# Text chunk settings
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150

# Retrieval
TOP_K = 6