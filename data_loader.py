# data_loader.py

from typing import List
import os
from dotenv import load_dotenv
from openai import OpenAI
from llama_index.readers.file import PDFReader
from llama_index.core.node_parser import SentenceSplitter


# --------------------------------------------------
# Load Environment Variables
# --------------------------------------------------
load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

if not OPENROUTER_API_KEY:
    raise ValueError("OPENROUTER_API_KEY not found in .env file")


# --------------------------------------------------
# Initialize OpenRouter Client (OpenAI-compatible)
# --------------------------------------------------
client = OpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1",
)


# --------------------------------------------------
# Embedding Configuration
# --------------------------------------------------
# Use OpenRouter compatible model naming
EMBED_MODEL = "openai/text-embedding-3-large"
EMBED_DIM = 3072


# --------------------------------------------------
# Splitter for Chunking
# --------------------------------------------------
splitter = SentenceSplitter(
    chunk_size=1000,
    chunk_overlap=200
)


# --------------------------------------------------
# Load + Chunk PDF
# --------------------------------------------------
def load_and_chunk_pdf(path: str) -> List[str]:
    """
    Load PDF file and split text into chunks using SentenceSplitter.
    """
    docs = PDFReader().load_data(file=path)
    texts = [getattr(d, "text", "") for d in docs if getattr(d, "text", None)]

    chunks: List[str] = []
    for t in texts:
        chunks.extend(splitter.split_text(t))

    return chunks


# --------------------------------------------------
# Generate Embeddings
# --------------------------------------------------
def embed_texts(texts: List[str]) -> List[List[float]]:
    """
    Generate embeddings for a list of texts using OpenRouter (OpenAI-compatible API).
    """
    response = client.embeddings.create(
        model=EMBED_MODEL,
        input=texts,
    )

    return [item.embedding for item in response.data]