# VaultRAG Architecture

## Current Version

v0.1 — Foundation

## Current Architecture

Client
  ↓
FastAPI application
  ↓
GET /health
  ↓
Health response

## Testing

FastAPI application
  ↓
TestClient
  ↓
pytest

## Future RAG Architecture

Client
  ↓
FastAPI
  ↓
RAG Pipeline
  ↓
Retriever
  ↓
Vector Store
  ↓
LLM
  ↓
Answer

## Current Version

v0.2 — Document Loading

## Current Architecture

Knowledge File
    ↓
Document Loader
    ↓
Text Content

Current application API:

Client
    ↓
FastAPI
    ↓
GET /health

The document loader is currently an independent component.
It is not yet connected to FastAPI or the RAG pipeline.

## Testing

FastAPI
    ↓
TestClient
    ↓
pytest

Document Loader
    ↓
pytest



## Ingestion Pipeline

Knowledge File
    ↓
Text Loader
    ↓
Raw Text
    ↓
Text Chunker
    ↓
Text Chunks
    ↓
Document Builder
    ↓
Document Objects
    ├── page_content
    └── metadata

Current metadata:

- source
- chunk_id

Future metadata may include:

- document_id
- department
- role/access level
- document type
- version
- created_at





VaultRAG/
├── app/
│   ├── main.py
│   ├── core/
│   │   └── config.py             # New
│   ├── ingestion/
│   │   ├── __init__.py
│   │   ├── loader.py             # Existing
│   │   ├── chunker.py            # Existing
│   │   ├── models.py             # Upgrade
│   │   └── document_builder.py   # Upgrade
│   └── services/
│       ├── __init__.py           # New
│       └── ingestion_service.py  # New
├── data/
│   └── documents/
├── tests/
│   ├── test_ingestion_service.py # New
│   └── ...
└── docs/



## Ingestion Service

Input:
- A text file inside the configured documents directory.

Pipeline:
1. Validate file path and extension.
2. Load text.
3. Generate stable source identity.
4. Calculate content hash.
5. Split text into chunks.
6. Build validated Document objects.

Output:
- A list of Document objects.
- Each document contains page_content and metadata.

Current metadata:
- source
- document_id
- content_hash
- chunk_id
- chunk_count

Limitations:
- TXT files only.
- No persistent storage yet.
- No embedding generation yet.
- No authentication or RBAC enforcement yet.



## Embedding Layer

The embedding layer converts document chunks and user queries into numerical
vectors through a provider-independent interface.

Components:
- `app/embeddings/base.py`: embedding provider contract.
- `app/embeddings/config.py`: batch configuration.
- `app/services/embedding_service.py`: batching and vector validation.

The service validates vector dimensions, numeric values, and provider output
counts. It does not depend on a specific model or vector database.

Current limitation:
- No real embedding provider is configured yet.
- The fake provider is used only in unit tests.
- Embeddings are not persisted or used for retrieval yet.