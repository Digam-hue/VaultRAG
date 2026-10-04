# VaultRAG

## Project Goal

VaultRAG is an enterprise knowledge assistant that will gradually evolve from a simple Retrieval-Augmented Generation (RAG) system into an adaptive, permission-aware and production-oriented AI system.

The project is being built from basic concepts first and progressively improved.

## Development Philosophy

- Start simple.
- Understand every component before increasing complexity.
- Build one component at a time.
- Keep components modular.
- Make components independently testable.
- Use FastAPI from the beginning.
- Gradually introduce advanced RAG and agentic techniques.
- Evaluate improvements instead of adding techniques only for complexity.
- Avoid premature production abstractions.

## Planned Evolution

Basic RAG
→ Modular RAG
→ FastAPI
→ Retrieval experiments
→ Evaluation
→ Permission-aware RAG
→ LangGraph
→ Adaptive RAG
→ Corrective RAG
→ Self-RAG
→ Agentic RAG
→ Memory
→ Human-in-the-loop
→ Observability
→ Docker
→ Deployment



### Current State — End of Day 7

VaultRAG has a configurable ingestion pipeline, document metadata models, a provider-independent embedding service, and a Hugging Face hosted embedding provider.

FastAPI exposes `POST /embeddings/query` for generating query vectors. The endpoint is manually testable through `/docs`.

**Current embedding model:** `BAAI/bge-small-en-v1.5` (configurable through `HF_EMBEDDING_MODEL`).

**Credentials:** Hugging Face token is stored in the local `.env` file. The Groq API key is reserved for the later answer-generation stage. Neither key should be committed to Git.

**Testing:** Unit tests and API tests are maintained separately from manual real-provider integration checks. Record their verified status before declaring Day 7 complete.

**Not implemented yet:** Persistent vector storage, semantic retrieval, retrieval-grounded answer generation, and permission-aware retrieval.

### Current State — End of Day 8

VaultRAG now includes document ingestion and chunking, metadata-bearing document models, a real Hugging Face embedding provider, persistent ChromaDB storage, indexing orchestration, and semantic retrieval.

**API endpoints**

* `POST /embeddings/query`: Generate an embedding for a question.
* `POST /ingestion/index`: Index a TXT file from the configured documents directory.
* `POST /retrieval/search`: Retrieve relevant chunks from the persistent vector store.

**Storage configuration:** `VECTOR_STORE_DIR` controls the ChromaDB persistence directory. Indexing and retrieval must use the same directory and collection.

**Current limitation:** Retrieval returns text passages and similarity distances; it does not yet generate a final answer using Groq. Permission-aware retrieval and production-grade document update/deletion handling remain future work.

Record the actual test and manual verification results before declaring Day 8 complete.
