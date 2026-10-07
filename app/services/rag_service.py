from app.services.generation_service import GenerationService
from app.services.retrieval_service import RetrievalService


class RAGService:
    """Coordinate retrieval and grounded answer generation."""

    def __init__(
        self,
        retrieval_service: RetrievalService,
        generation_service: GenerationService,
    ) -> None:
        self.retrieval_service = retrieval_service
        self.generation_service = generation_service

    def ask(
        self,
        question: str,
        top_k: int = 5,
    ) -> dict:
        if not question.strip():
            raise ValueError("Question cannot be empty")

        documents = self.retrieval_service.search(
            question=question,
            top_k=top_k,
        )

        answer = self.generation_service.generate_answer(
            question=question,
            documents=documents,
        )

        return {
            "question": question,
            "answer": answer,
            "sources": documents,
        }