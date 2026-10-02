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