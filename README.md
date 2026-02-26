# Secure RAG Lab 🛡️

A secure-by-design Retrieval-Augmented Generation pipeline using FastAPI, LangChain, and FAISS.

## Architecture Diagram

```mermaid
graph TD
    A[User] --> B[FastAPI Endpoint]
    B --> C{Input Validation}
    C -->|Sanitized| D[Embed Query]
    D --> E[FAISS Vector Store]
    E --> F[Context Filter / Redaction]
    F --> G[Secure Prompt Template]
    G --> H[OpenAI LLM]
    H --> I{Output Filter}
    I -->|Safe| J[User Response]
    C -->|Invalid| K[Error 400]