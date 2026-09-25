
## 🛡️ RAG Security & Threat Assessment Report

### 1. Executive Summary
This assessment evaluates the threat surface of the containerized RAG pipeline, covering document intake, embedding generation, vector persistence in Qdrant, and prompt construction. Because the assistant processes untrusted external PDF documents (such as third-party CVE advisories and threat research), the primary risks center on context manipulation, cross-session data bleeding, and unauthorized vector store manipulation.

### 2. Ingestion & Retrieval Attack Surface Analysis
- **PDF Ingestion & Parsing Boundary:** Binary parsing and text extraction handle untrusted input streams. Malicious formatting or embedded hidden text layers within PDFs can bypass naive text extraction filters.
- **Vector Index Storage:** Embeddings stored in Qdrant lack tenant-level encryption if running on default local port configurations without authentication tokens.
- **Prompt Augmentation Layer:** Retrieved text chunks are interpolated into the base prompt template. Without strict contextual boundary delimiters, untrusted chunk text can blend directly with instruction space.

### 3. Threat Vector Breakdown

#### Indirect Prompt Injection (Data Poisoning in Vector Store)
- **Mechanism:** An uploaded PDF contains adversarially crafted text blocks (e.g., hidden white-on-white text or injected instructions) designed to mimic system commands. When a user asks a query matching those vectors, the malicious chunks are retrieved and loaded into the LLM context window, instructing the model to disregard prior instructions or alter its analysis.
- **Impact:** Misdirection of vulnerability assessments, suppression of reported CVEs, or unauthorized execution of unintended output formatting.

#### Cross-Tenant Retrieval & Context Bleed
- **Mechanism:** When multiple analyst sessions or teams upload documents into a shared Qdrant collection without partition keys or metadata-based tenant segregation, semantic similarity queries can surface sensitive findings across document boundaries.
- **Impact:** Unauthorized internal disclosure of proprietary red team findings, client identifiers, or zero-day vulnerability disclosures.

#### Unauthorized API / Vector DB Access
- **Mechanism:** Qdrant instances exposed on default ports (`6333`/`6334`) without mandatory API key enforcement or TLS transport encryption allow unauthenticated internal network actors to read, overwrite, or delete collection embeddings.
- **Impact:** Complete database exfiltration, vector store poisoning, or loss of ingestion data integrity.

### 4. Prioritized Defensive Hardening Plan

| Priority | Category | Target Component | Remediation Strategy |
| :--- | :--- | :--- | :--- |
| **P0 (Critical)** | Prompt Isolation | Prompt Construction | Wrap retrieved context in structural delimiters (e.g., `<context>` tags) and instruct the system prompt to treat all context content as untrusted data rather than operational instructions. |
| **P0 (Critical)** | Access Control | Qdrant Engine | Enforce API keys via `service.api_key` in Qdrant configuration and bind listener ports strictly to localhost or private Docker networks. |
| **P1 (High)** | Collection Partitioning | Retrieval Logic | Implement strict metadata filtering on every similarity search (e.g., `user_id`, `tenant_id`, `document_id`) to prevent cross-tenant context bleed. |
| **P1 (High)** | Automated Testing | Promptfoo Pipeline | Maintain continuous regression test matrices in `promptfoo.yaml` to evaluate model resilience against known indirect injection vectors. |
| **P2 (Medium)** | Input Sanitization | PDF Loader | Strip non-printable characters, inspect raw PDF streams for script execution anomalies, and enforce strict file-size limits prior to chunking. |

---

## 🚀 Running the Project

### 1. Prerequisites
- Docker (for Qdrant)
- Node.js (for Inngest CLI)[cite: 18]
- Python 3.10+[cite: 18]

### 2. Setup Environment
```bash
git clone [https://github.com/SlatX/RAG-project.git](https://github.com/SlatX/RAG-project.git)
cd RAG-project
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
