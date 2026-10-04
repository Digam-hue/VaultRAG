from pathlib import Path

from app.services.embedding_service import EmbeddingService
from app.services.ingestion_service import IngestionService
from app.vectorstore.base import VectorStore


class IndexingService:
    """Ingest documents, generate embeddings, and store searchable chunks."""

    def __init__(
        self,
        ingestion_service: IngestionService,
        embedding_service: EmbeddingService,
        vector_store: VectorStore,
    ) -> None:
        self.ingestion_service = ingestion_service
        self.embedding_service = embedding_service
        self.vector_store = vector_store

    def index_file(self, file_path: Path) -> dict:
        documents = self.ingestion_service.ingest_file(file_path)

        if not documents:
            raise ValueError("The document produced no searchable chunks")

        embeddings = self.embedding_service.embed_documents(documents)

        self.vector_store.add_documents(
            documents=documents,
            embeddings=embeddings,
        )

        return {
            "source": documents[0].metadata["source"],
            "document_id": documents[0].metadata["document_id"],
            "chunks_indexed": len(documents),
        }