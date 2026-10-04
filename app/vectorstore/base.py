
from typing import Protocol, Sequence

from app.embeddings.base import EmbeddingVector
from app.ingestion.models import Document


class VectorStore(Protocol):
    """Contract for storing and searching embedded documents."""

    def add_documents(
        self,
        documents: Sequence[Document],
        embeddings: Sequence[EmbeddingVector],
    ) -> None:
        ...

    def similarity_search(
        self,
        query_embedding: EmbeddingVector,
        top_k: int = 5,
    ) -> list[dict]:
        ...