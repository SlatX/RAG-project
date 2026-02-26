from typing import List, Optional
from pydantic import BaseModel

class RAGChunkAndSrc(BaseModel):
    chunks: List[str]                  # List of text chunks
    source_id: Optional[str] = None    # Optional source identifier

class RAGUpsertResult(BaseModel):
    ingested: int                      # Number of chunks ingested

class RAGSearchResult(BaseModel):
    contexts: List[str]                 # Retrieved text contexts
    sources: List[str]                  # Corresponding sources for contexts

class RAQQueryResult(BaseModel):
    answer: str                         # Generated answer
    sources: List[str]                  # Sources used for the answer
    num_contexts: int                    # Number of contexts used