# Changelog

## 2026-09-30

### Added

- Initialized VaultRAG project.
- Created initial application, test and document directories.
- Created Python virtual environment.
- Added FastAPI and Uvicorn.
- Added initial project documentation.


## 2026-09-30 — Day 2

### Added

- Created `app/ingestion/` module.
- Added first knowledge document.
- Implemented basic text document loader.
- Added document loader unit test.

### Tests

- All tests passing.



## Day 4 — Document Model and Metadata

### Added

- Document data model using dataclass.
- Metadata support for ingested chunks.
- Document builder component.
- Source and chunk identifiers.
- Empty chunk filtering.

### Tests

- Added Document model tests.
- Added document builder tests.
- All tests passing.



## Day 5 — Ingestion Service

### Added
- IngestionConfig with validation.
- Pydantic Document model.
- SHA-256 content hashing.
- Stable source-based document IDs.
- IngestionService to coordinate loading,
  chunking and document construction.
- Integration tests for success and failure cases.

### Security and limitations
- Restricted ingestion to the configured directory.
- Only TXT files are supported.
- No database persistence or RBAC enforcement yet.




## Decision: Ingestion Service

- Keep ingestion logic independent of FastAPI.
- Inject the documents directory and configuration.
- Use Pydantic for configuration and document validation.
- Use a stable source identity and a separate content hash.
- Keep components independently testable.
- Start with local TXT ingestion before adding more formats.



## Day 6 — Embedding Layer

Added a provider-independent embedding service with batch processing,
vector validation, and test coverage using a lightweight fake provider.

No production embedding model or vector database has been connected yet.


## Day 7 — Embedding API

* Added a Hugging Face embedding provider using hosted inference.
* Connected real embeddings to the existing embedding service.
* Added `POST /embeddings/query` to FastAPI.
* Added request validation and response schema.
* Added API tests for successful responses and invalid inputs.
* Kept automated tests independent of external API availability.
