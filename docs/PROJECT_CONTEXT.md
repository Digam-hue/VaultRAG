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









## Current State — End of Day 11

VaultRAG has a working modular RAG foundation with document ingestion,
chunking, embeddings, persistent ChromaDB storage, semantic retrieval,
Groq-based answer generation, and the `POST /rag/ask` endpoint.

Day 11 focuses on reliability testing:
- RAG service integration-style tests.
- Empty retrieval behavior.
- API request validation.
- Expected and unexpected error handling.
- Provider contract tests using mocks.

Latest confirmed full-suite result: 54 passed.
Latest reported application coverage: 78%.

Before starting the next implementation phase, run the complete test
suite and record the final results after provider contract tests.

### Resume Instructions

1. Activate `.venv`.
2. Run `python -m pytest -q`.
3. Run `python -m pytest --cov=app --cov-report=term-missing`.
4. Check `git status` and commit the completed Day 11 changes.
5. Continue with the next planned RAG milestone; do not add RBAC,
   LangGraph, or multi-agent complexity prematurely.

## Current Status — Day 12 Complete

VaultRAG now supports internal permission-aware retrieval.

Implemented:
- Access-level metadata during document creation.
- Access-level propagation through ingestion and indexing.
- Optional access-level filtering during vector-store retrieval.
- Access-level propagation through the RAG service.
- Automated tests for permission-aware retrieval and propagation.

Not implemented yet:
- Access-level input in FastAPI indexing routes.
- Permission-related request models and API responses.
- Authentication and role-based authorization.
- Deriving retrieval permissions from the authenticated user.

Next:
Expose document access levels through the API, verify the workflow
using FastAPI /docs, and then build trusted authentication and
authorization into the system.