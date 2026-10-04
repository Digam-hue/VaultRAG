from app.services.embedding_service import EmbeddingService
from app.vectorstore.base import VectorStore


class RetrievalService:
    """Generate query embeddings and retrieve relevant document chunks."""

    def __init__(
        self,
        embedding_service: EmbeddingService,
        vector_store: VectorStore,
    ) -> None:
        self.embedding_service = embedding_service
        self.vector_store = vector_store

    def search(
        self,
        question: str,
        top_k: int = 5,
    ) -> list[dict]:
        if not question.strip():
            raise ValueError("Question cannot be empty")

        if top_k <= 0:
            raise ValueError("top_k must be greater than zero")

        query_embedding = self.embedding_service.embed_query(question)

        return self.vector_store.similarity_search(
            query_embedding=query_embedding,
            top_k=top_k,
        )