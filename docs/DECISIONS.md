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