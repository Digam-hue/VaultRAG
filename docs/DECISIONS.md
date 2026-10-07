# VaultRAG Architecture Decisions

## Decision 001 — Start with a simple architecture

### Decision

VaultRAG will begin with a minimal project structure and gradually become more sophisticated.

### Reason

The goal is to understand each component rather than starting with a production architecture that hides the underlying concepts.

---

## Decision 002 — FastAPI from the beginning

### Decision

FastAPI will be introduced from the first working version.

### Reason

The final system will be an API-based AI application, so API development should be learned alongside the RAG system rather than added only at the end.

---

## Decision 003 — Test components independently

### Decision

Each important component should eventually have its own tests.

### Reason

This allows us to identify whether a problem comes from loading, chunking, embedding, retrieval, generation, or API integration.



## Embedding Provider Abstraction

Decision:
Keep model-specific behavior behind an embedding provider interface.

Reasons:
- Avoid coupling retrieval to one embedding model.
- Permit local and hosted providers to be evaluated separately.
- Test batching and validation without downloading a model.
- Validate vector dimensions before vectors reach storage.

Trade-off:
A provider implementation is still required before real semantic search
can work.



## Decision — Hosted Embedding Provider

**Decision:** Use a provider interface with a Hugging Face hosted inference implementation for the initial embedding integration.

**Reasoning:** Hosted inference avoids requiring model weights and heavy inference dependencies on the development laptop. The provider can be replaced without redesigning the embedding service.

**Trade-offs:** Requires network access, valid credentials, model/provider availability, and compliance with inference quotas or pricing limits.

**Security:** Credentials are supplied through environment configuration and must not be committed or returned by API endpoints.

**Future consideration:** Evaluate a multilingual model if the knowledge base requires multilingual retrieval.
git






## Decision — Initial Vector Store

**Decision:** Use ChromaDB with persistent local storage for the initial VaultRAG retrieval implementation.

**Reasoning:** It provides a straightforward way to store embeddings, text, and metadata while learning and validating the RAG pipeline.

**Trade-offs:** Local persistence is convenient for development but requires careful configuration for deployment, backups, concurrent access, and authorization filtering.

**Future consideration:** Reassess ChromaDB versus Qdrant or PostgreSQL with pgvector when deployment and permission-aware retrieval requirements are implemented.

Document replacement:
Re-indexing uses document_id to remove all previously indexed chunks before
storing the new version. This prevents stale chunks from an older document
version remaining in the vector store.