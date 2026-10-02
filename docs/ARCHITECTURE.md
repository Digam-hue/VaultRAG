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