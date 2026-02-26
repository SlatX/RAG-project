import os
import uuid
import logging
import datetime
import re
from pathlib import Path

from fastapi import FastAPI
from dotenv import load_dotenv
import inngest
import inngest.fast_api
from inngest.experimental import ai

from data_loader import load_and_chunk_pdf, embed_texts
from vector_db import QdrantStorage
from custom_types import RAGChunkAndSrc, RAGUpsertResult, RAGSearchResult

# ---------------- ENV ----------------
load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    raise ValueError("OPENROUTER_API_KEY not found in .env")

# ---------------- LOGGING ----------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("secure_rag")

# ---------------- SECURITY ----------------
MAX_QUERY_LENGTH = 500
BLOCK_PATTERNS = [
    r"ignore previous instructions",
    r"reveal system prompt",
    r"you are now",
    r"act as",
    r"override",
    r"disregard",
]
ALLOWED_PDF_DIRECTORY = Path("./data").resolve()

def validate_user_input(text: str) -> str:
    if len(text) > MAX_QUERY_LENGTH:
        raise ValueError("Query too long")
    lowered = text.lower()
    for pattern in BLOCK_PATTERNS:
        if re.search(pattern, lowered):
            raise ValueError("Potential prompt injection detected")
    return text.strip()

def sanitize_context(text: str) -> str:
    for pattern in BLOCK_PATTERNS:
        text = re.sub(pattern, "", text, flags=re.I)
    return text.strip()

def validate_output(text: str) -> str:
    if any(k in text.lower() for k in ["system prompt", "api key"]):
        raise ValueError("Unsafe output detected")
    return text.strip()

def validate_pdf_path(pdf_path: str) -> Path:
    resolved = Path(pdf_path).resolve()
    if not str(resolved).startswith(str(ALLOWED_PDF_DIRECTORY)):
        raise ValueError("Invalid PDF path")
    return resolved

# ---------------- INNGEST ----------------
inngest_client = inngest.Inngest(
    app_id="secure-rag-app",
    logger=logging.getLogger("uvicorn"),
    is_production=False,
    serializer=inngest.PydanticSerializer()
)

# ---------------- PDF INGEST ----------------
@inngest_client.create_function(
    fn_id="secure-rag-ingest",
    trigger=inngest.TriggerEvent(event="rag/ingest_pdf"),
    throttle=inngest.Throttle(limit=2, period=datetime.timedelta(minutes=1))
)
async def rag_ingest_pdf(ctx: inngest.Context):

    def _load() -> RAGChunkAndSrc:
        pdf_path = validate_pdf_path(ctx.event.data["pdf_path"])
        source_id = ctx.event.data.get("source_id", str(pdf_path))
        chunks = load_and_chunk_pdf(str(pdf_path))
        return RAGChunkAndSrc(chunks=chunks, source_id=source_id)

    def _embed_store(data: RAGChunkAndSrc) -> RAGUpsertResult:
        vectors = embed_texts(data.chunks)
        ids = [str(uuid.uuid5(uuid.NAMESPACE_URL, f"{data.source_id}:{i}")) for i in range(len(data.chunks))]
        payloads = [{"source": data.source_id, "text": data.chunks[i]} for i in range(len(data.chunks))]
        QdrantStorage().upsert(ids, vectors, payloads)
        return RAGUpsertResult(ingested=len(data.chunks))

    chunks = await ctx.step.run("load-pdf", _load, output_type=RAGChunkAndSrc)
    result = await ctx.step.run("embed-store", lambda: _embed_store(chunks), output_type=RAGUpsertResult)
    return result.model_dump()

# ---------------- QUERY ----------------
@inngest_client.create_function(
    fn_id="secure-rag-query",
    trigger=inngest.TriggerEvent(event="rag/query_pdf_ai"),
    throttle=inngest.Throttle(limit=10, period=datetime.timedelta(minutes=1))
)
async def rag_query_pdf_ai(ctx: inngest.Context):
    question = validate_user_input(ctx.event.data["question"])
    top_k = int(ctx.event.data.get("top_k", 5))

    def _search() -> RAGSearchResult:
        query_vector = embed_texts([question])[0]
        store = QdrantStorage()
        found = store.search(query_vector, top_k)
        cleaned_contexts = [sanitize_context(c) for c in found["contexts"]]
        return RAGSearchResult(contexts=cleaned_contexts, sources=found["sources"])

    found = await ctx.step.run("embed-search", _search, output_type=RAGSearchResult)
    context_block = "\n\n".join(f"- {c}" for c in found.contexts)
    user_prompt = f"""
Use ONLY the context below to answer.

Context:
{context_block}

Question:
{question}

If answer is not in context, say:
"Information not available."
"""

    adapter = ai.openai.Adapter(auth_key=OPENROUTER_API_KEY, model="openai/gpt-4o-mini", base_url="https://openrouter.ai/api/v1")
    response = await ctx.step.ai.infer("generate-answer", adapter=adapter, body={
        "max_tokens": 1024,
        "temperature": 0.2,
        "messages":[
            {"role":"system","content":"You are a secure RAG assistant."},
            {"role":"user","content":user_prompt}
        ]
    })
    answer_raw = response["choices"][0]["message"]["content"]
    answer = validate_output(answer_raw)
    return {"answer": answer, "sources": found.sources, "num_contexts": len(found.contexts)}

# ---------------- FASTAPI ----------------
app = FastAPI()
inngest.fast_api.serve(app, inngest_client, [rag_ingest_pdf, rag_query_pdf_ai])