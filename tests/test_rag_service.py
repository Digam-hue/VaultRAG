from app.services.rag_service import RAGService


class FakeRetrievalService:
    def __init__(self):
        self.questions = []

    def search(self, question: str, top_k: int = 5):
        self.questions.append((question, top_k))

        return [
            {
                "page_content": "Employees receive 30 days of annual leave.",
                "metadata": {
                    "source": "leave_policy.txt",
                },
                "distance": 0.1,
            }
        ]


class FakeGenerationService:
    def __init__(self):
        self.requests = []

    def generate_answer(self, question: str, documents):
        self.requests.append((question, documents))

        return "Employees receive 30 days of annual leave."


def test_rag_service_coordinates_retrieval_and_generation():
    retrieval_service = FakeRetrievalService()
    generation_service = FakeGenerationService()

    service = RAGService(
        retrieval_service=retrieval_service,
        generation_service=generation_service,
    )

    result = service.ask(
        question="How many annual leave days are provided?",
        top_k=3,
    )

    assert result["answer"] == (
        "Employees receive 30 days of annual leave."
    )

    assert result["question"] == (
        "How many annual leave days are provided?"
    )

    assert len(result["sources"]) == 1

    assert retrieval_service.questions == [
        ("How many annual leave days are provided?", 3)
    ]

    assert len(generation_service.requests) == 1