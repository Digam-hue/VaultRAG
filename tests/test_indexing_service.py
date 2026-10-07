from pathlib import Path

from app.ingestion.models import Document
from app.services.indexing_service import IndexingService


class FakeIngestionService:
    def ingest_file(self, file_path: Path) -> list[Document]:
        return [
            Document(
                page_content="Annual leave policy",
                metadata={
                    "source": file_path.name,
                    "document_id": "test-doc-1",
                    "content_hash": "hash-1",
                    "chunk_id": "0",
                    "chunk_count": 1,
                },
            )
        ]


class FakeEmbeddingService:
    def embed_documents(self, documents):
        return [[0.1, 0.2, 0.3] for _ in documents]


class FakeVectorStore:
    def __init__(self):
        self.deleted_document_ids = []
        self.documents = []
        self.embeddings = []

    def delete_document(self, document_id: str) -> None:
        self.deleted_document_ids.append(document_id)

    def add_documents(self, documents, embeddings) -> None:
        self.documents = list(documents)
        self.embeddings = list(embeddings)


def test_index_file_replaces_existing_document():
    ingestion_service = FakeIngestionService()
    embedding_service = FakeEmbeddingService()
    vector_store = FakeVectorStore()

    service = IndexingService(
        ingestion_service=ingestion_service,
        embedding_service=embedding_service,
        vector_store=vector_store,
    )

    result = service.index_file(Path("leave_policy.txt"))

    assert result == {
        "source": "leave_policy.txt",
        "document_id": "test-doc-1",
        "chunks_indexed": 1,
    }

    assert vector_store.deleted_document_ids == ["test-doc-1"]

    assert len(vector_store.documents) == 1
    assert len(vector_store.embeddings) == 1