# 🔐 Cybersecurity RAG PDF Assistant

A Retrieval-Augmented Generation (RAG) application that allows users to upload PDF documents and ask questions about their content.

Built to improve analysis workflows for cybersecurity reports, threat intelligence, vulnerability disclosures, and red team documentation.

---

## 🎯 Project Goal

This project was created to:

- Ingest PDF documents  
- Convert them into vector embeddings  
- Store embeddings in a vector database  
- Retrieve relevant context for user queries  
- Generate accurate, context-aware answers using an LLM  

Instead of manually searching long security reports, users can ask targeted questions and receive grounded AI-assisted answers.

---

# 🏗️ Architecture Diagram

                 ┌────────────────────────┐
                 │     PDF Documents      │
                 │ (Reports / Intel / CVE)│
                 └─────────────┬──────────┘
                               │
                               ▼
                 ┌────────────────────────┐
                 │   PDF Loader &         │
                 │   Text Chunking        │
                 └─────────────┬──────────┘
                               │
                               ▼
                 ┌────────────────────────┐
                 │   Embedding Model      │
                 │   (OpenAI API)         │
                 └─────────────┬──────────┘
                               │
                               ▼
                 ┌────────────────────────┐
                 │   Qdrant Vector DB     │
                 │   (Semantic Storage)   │
                 └─────────────┬──────────┘
                               │
                User Query     │
                ───────────►   ▼
                 ┌────────────────────────┐
                 │   Query Embedding      │
                 └─────────────┬──────────┘
                               │
                               ▼
                 ┌────────────────────────┐
                 │   Top-K Similarity     │
                 │   Search               │
                 └─────────────┬──────────┘
                               │
                               ▼
                 ┌────────────────────────┐
                 │   Context-Augmented    │
                 │   Prompt (RAG)         │
                 └─────────────┬──────────┘
                               │
                               ▼
                 ┌────────────────────────┐
                 │   LLM Response         │
                 └─────────────┬──────────┘
                               │
                               ▼
                 ┌────────────────────────┐
                 │   Streamlit Interface  │
                 │   + Source Display     │
                 └────────────────────────┘

---

## 🛠 Tech Stack

- Python  
- Streamlit  
- Qdrant (Vector Database)  
- Inngest (Event-driven ingestion)  
- OpenAI API  
- Promptfoo (LLM evaluation & testing)

---

## 🚀 Running the Project

1. Install dependencies:

2. Add your API key in a `.env` file:

3. Start required services (Qdrant + Inngest)

4. Run the application:

---

## 🔎 Example Use Cases

- “Summarize the vulnerabilities mentioned in this report.”
- “Extract indicators of compromise from this document.”
- “What CVEs are referenced in this advisory?”
- “Explain the attack chain described in this red team report.”

---

## 🔐 Security Notes

- `.env` is excluded from Git  
- Raw data and vector storage are not committed  
- Designed for controlled research environments  

---

## 👤 Author

Ebenezer  
Cybersecurity & AI Security Enthusiast