# Quality Standard Specification: Threat Baseline (OWASP Top 10 for LLMs)

**Document Identifier:** `threat_baseline.md`  
**Standard Authority:** [OWASP Top 10 for Large Language Model Applications](https://genai.owasp.org/llm-top-10/)  
**Classification:** Quality Standard & Architectural Baseline  
**Target Architecture:** Retrieval-Augmented Generation (RAG) & Document Processing Systems  

---

## 1. Executive Standard Overview

This document defines the baseline security standard and threat-modeling criteria for LLM-powered applications and Retrieval-Augmented Generation (RAG) pipelines. LLMs shift the trust boundary by intermingling user control instructions and untrusted data within a single natural language context. All pipelines ingesting, vectorizing, and retrieving external documents must satisfy this baseline prior to architectural approval.

---

## 2. Standard OWASP Top 10 for LLM Applications Register

| Vulnerability ID | Vulnerability Name | Threat Vector & Primary Impact | Baseline Severity |
| :--- | :--- | :--- | :--- |
| **LLM01** | **Prompt Injection** | Crafting direct or indirect inputs to manipulate model context and bypass safeguards. | **Critical** |
| **LLM02** | **Sensitive Information Disclosure** | Leaking confidential proprietary data, secrets, or PII through model completions. | **Critical** |
| **LLM03** | **Supply Chain Vulnerabilities** | Using vulnerable base weights, malicious pre-trained models, or poisoned packages. | **High** |
| **LLM04** | **Data and Model Poisoning** | Adversarial tampering during pre-training, fine-tuning, or embedding ingestion. | **High** |
| **LLM05** | **Improper Output Handling** | Executing unsanitized model outputs in downstream consumers (XSS, SQLi, SSRF). | **High** |
| **LLM06** | **Excessive Agency** | Granting models unrestricted tools, excessive API scopes, or high permissions without verification. | **High** |
| **LLM07** | **System Prompt Leakage** | Eliciting sensitive operational instructions, hidden schemas, or secrets via crafted queries. | **Medium** |
| **LLM08** | **Vector and Embedding Weaknesses** | Exploiting vector database vulnerabilities, context poisoning, or performing embedding inversion. | **Critical** |
| **LLM09** | **Misinformation** | Producing fabricated, hallucinated, or biased outputs treated as verified facts. | **Medium** |
| **LLM10** | **Unbounded Consumption** | Exploiting token usage, computational complexity, or unbounded context to cause DoS. | **Medium** |

---

## 3. High-Priority Threat Deep Dives

### 3.1 LLM01: Prompt Injection

Prompt Injection occurs when untrusted input alters model execution logic, compelling the system to disregard system directives, execute unauthorized tasks, or bypass security guardrails.

#### Threat Vectors & Manifestations
- **Direct Injection (Jailbreaking):** Explicit user prompts designed to overwrite system roles using hypothetical framing, virtualization, linguistic obfuscation, or persona adoption.
- **Indirect Prompt Injection:** Adversarial instructions placed inside external untrusted data ingested by the RAG pipeline (e.g., hidden text, zero-point fonts, metadata tags, or poisoned vulnerability advisories inside uploaded PDFs).
- **Multimodal Payload Delivery:** Obfuscated instructions embedded in document attachments, image channels, or metadata attributes parsed by multimodal models.

#### Mandatory Baseline Mitigations
1. **Context & Instruction Demarcation:** Enforce structural token boundaries and delimiters (e.g., `<context>...</context>`) while explicitly instructing the model to treat retrieved content as passive reference data rather than executable directives.
2. **Dual-LLM / Classifier Guardrails:** Inspect incoming queries and raw retrieved text chunks using lightweight safety classifiers before passing them to the primary inference engine.
3. **Privilege & Tool Scoping:** Restrict downstream tool execution to read-only capabilities and mandate human-in-the-loop authorization for sensitive operations.

---

### 3.2 LLM02: Sensitive Information Disclosure

Sensitive Information Disclosure occurs when an LLM emits confidential proprietary intellectual property, Personal Identifiable Information (PII), credentials, or internal configuration data in its responses.

#### Threat Vectors & Manifestations
- **Training Data Memorization & Extraction:** Attackers use crafted extraction prompts to trigger model verbatim recall of confidential training or fine-tuning datasets.
- **Inadvertent RAG Retrieval:** Over-permissive similarity search queries retrieve documents outside the requesting user's authorization level, injecting sensitive excerpts into the model context window.
- **Context Bleed Across Sessions:** Shared memory caches or multi-tenant conversational state leakage exposing another user's queries or retrieved excerpts.

#### Mandatory Baseline Mitigations
1. **Pre-Ingestion PII & Secret Scrubbing:** Enforce automated redaction pipelines (e.g., regex patterns, Presidio, token masking) on document text prior to vector generation.
2. **Document-Level Access Controls (DLAC):** Bind permissions to document vectors and enforce access verification before context chunks are injected into the prompt.
3. **Output Egress Filtering:** Implement real-time Data Loss Prevention (DLP) checks on generated responses to detect and block API keys, tokens, and sensitive data patterns.

---

### 3.3 LLM08: Vector and Embedding Weaknesses

Vector and embedding weaknesses arise when untrusted documents are translated into high-dimensional mathematical representations and indexed in vector databases (such as Qdrant, Pinecone, or Milvus).

#### Threat Vectors & Manifestations
- **RAG Context Poisoning (Vector Space Poisoning):** An attacker crafts text passages with semantic patterns engineered to achieve high cosine similarity for specific target queries, displacing legitimate contextual data during top-$k$ retrieval.
- **Embedding Inversion Attacks:** Threat actors mathematically reconstruct original text chunks or sensitive information directly from raw stored vectors.
- **Cross-Tenant Retrieval & Context Bleed:** Multi-tenant vector databases lacking strict namespace or payload partitioning, allowing similarity searches to pull embeddings belonging to other tenants.
- **Semantic Clustering Manipulation:** Forcing adversarial groupings that steer summarization, sentiment analysis, or contextual classification away from objective truth.

#### Mandatory Baseline Mitigations
1. **Enforced Payload Filtering:** Embed tenant and authorization identifiers directly into vector payload metadata and mandate non-strippable filtering predicates on every similarity search:
   ```python
   # Example: Enforced Qdrant Payload Filter
   from qdrant_client.http import models

   search_filter = models.Filter(
       must=[
           models.FieldCondition(
               key="tenant_id",
               match=models.MatchValue(value=current_user.tenant_id),
           ),
           models.FieldCondition(
               key="access_tier",
               range=models.Range(lte=current_user.access_tier),
           ),
       ]
   )
   ```
2. **Vector Store Broker Abstraction:** Never expose raw vector database ports directly to clients or public networks; isolate the database behind authenticated internal APIs.
3. **Cryptographic Chunk Verification:** Calculate and store SHA-256 hashes of original text chunks to ensure document integrity and detect unauthorized vector database alterations.

---

## 4. Verification & Audit Matrix

| Verification ID | Focus Area | Verification Activity | Operational Quality Gate |
| :--- | :--- | :--- | :--- |
| **VERIF-LLM-01** | LLM01 | Automated red-teaming fuzzing using Promptfoo across direct jailbreaks and indirect PDF payloads. | Zero prompt overrides or security boundary bypasses. |
| **VERIF-LLM-02** | LLM02 | Ingestion testing with synthetic canary credentials and PII patterns to test egress filters. | 100% detection and redaction of canary secrets. |
| **VERIF-LLM-08A** | LLM08 | Multi-tenant query boundary testing across isolated document partitions. | Complete isolation; zero cross-tenant retrieval events. |
| **VERIF-LLM-08B** | LLM08 | Cosine distance distribution analysis to flag adversarial outlier vector clusters. | Automated quarantine of anomalous similarity spikes. |
