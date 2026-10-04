
from pathlib import Path

from app.ingestion.models import Document
from app.services.indexing_service import IndexingService


class FakeIngestionService:
    def ingest_file(self, file_path: Path):
        return [
            Document(
                page_content="The leave policy allows 20 days.",
                metadata={
                    "source": file_path.name,
                    "document_id": "doc-1",
                    "content_hash": "hash-1",
                    "chunk_id": 0,
                    "chunk_count": 1,
                },
            )
        ]


class FakeEmbeddingService:
    def embed_documents(self, documents):
        assert len(documents) == 1
        return [[0.1, 0.2, 0.3]]


class FakeVectorStore:
    def __init__(self):
        self.documents = []
        self.embeddings = []

    def add_documents(self, documents, embeddings):
        self.documents = list(documents)
        self.embeddings = list(embeddings)


def test_index_file_runs_complete_indexing_flow(tmp_path):
    vector_store = FakeVectorStore()

    service = IndexingService(
        ingestion_service=FakeIngestionService(),
        embedding_service=FakeEmbeddingService(),
        vector_store=vector_store,
    )

    result = service.index_file(tmp_path / "handbook.txt")

    assert result["source"] == "handbook.txt"
    assert result["document_id"] == "doc-1"
    assert result["chunks_indexed"] == 1
    assert len(vector_store.documents) == 1
    assert vector_store.embeddings == [[0.1, 0.2, 0.3]]