# System Architecture & Technical Specification

## 1. Technical Stack Overview
- **Backend Service:** FastAPI application exposing REST endpoints for document ingestion and retrieval.
- **Vector Database:** Qdrant instance deployed via Docker container (default ports 6333/6334) handling vector storage, payload metadata, and cosine similarity indexing.
- **Ingestion Pipeline:** PDF and raw document parsing, recursive character text chunking (fixed chunk size with overlap), and vector embedding generation via the embedding API.
- **Retrieval Engine:** Semantic top-k nearest neighbor similarity search against indexed vector collections.
- **Inference Pipeline:** Context-augmented prompt assembly dispatching combined context and query to the downstream LLM.

---

## 2. Ingestion & Retrieval Data Flow
1. **Document Processing:** Unstructured documents (advisories, CVE reports) are parsed into text, split into overlapping chunks, and mapped to vector embeddings.
2. **Persistence:** Embeddings and raw text segments are saved into Qdrant collections along with metadata (e.g., document ID, timestamp, source filename).
3. **Query Handling:** An incoming natural language question is embedded using the same vector model.
4. **Context Assembly:** Qdrant returns top-k matching text chunks. The application combines the retrieved text into a prompt template alongside system instructions and passes the payload to the LLM.

---

## 3. Trust Boundaries & Entry Points

### Trust Boundary A: The Ingestion Endpoint (`/ingest`)
- **Nature:** Untrusted / Semi-trusted file upload boundary.
- **Mechanism:** Accepts files directly from clients, runs extraction, and writes to database storage without multi-tenant privilege separation.
- **Exposure:** Subject to data poisoning and embedded indirect prompt injection vectors designed to manipulate retrieval results.

### Trust Boundary B: The Semantic Query Endpoint (`/query`)
- **Nature:** Untrusted user input boundary.
- **Mechanism:** Accepts raw user prompt strings to compute embeddings and query vector collections.
- **Exposure:** Subject to direct prompt injection, jailbreaking, and targeted similarity probes intended to surface confidential context chunks.

### Trust Boundary C: Prompt Template Assembly & LLM Context Boundary
- **Nature:** Internal execution boundary.
- **Mechanism:** Dynamically concatenates user input with untrusted retrieved database text chunks before dispatching to the LLM.
- **Exposure:** Lack of boundary delimiters or output sanitization allows malicious instructions in retrieved chunks to override system role instructions.

### Trust Boundary D: Vector Store Access & Network Boundary
- **Nature:** Infrastructure and container boundary.
- **Mechanism:** Docker container running Qdrant accessible over internal/external network ports.
- **Exposure:** Unauthenticated API access, lack of TLS encryption between application and Qdrant container, and missing tenant-level namespace enforcement.
