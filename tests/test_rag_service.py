from app.services.rag_service import RAGService
from app.services.generation_service import GenerationService
import pytest
class FakeRetrievalService:
    def __init__(self):
        self.questions = []
        self.received_access_levels = None


    def search(self, question: str, 
               top_k: int = 5,
               allowed_access_levels=None,):
        
        self.questions.append((question, top_k))
        self.received_access_levels = allowed_access_levels
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


class FakeLLMProvider:
    def __init__(self):
        self.prompts = []

    def generate(self, prompt: str) -> str:
        self.prompts.append(prompt)
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
    

def test_rag_service_passes_retrieved_context_to_generation():
    retrieval_service = FakeRetrievalService()
    llm_provider = FakeLLMProvider()
    generation_service = GenerationService(llm_provider)

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

    assert len(llm_provider.prompts) == 1

    prompt = llm_provider.prompts[0]

    assert "30 days of annual leave" in prompt
    assert "How many annual leave days are provided?" in prompt

    assert result["sources"][0]["metadata"]["source"] == (
        "leave_policy.txt"
    )



def test_rag_service_handles_no_retrieved_documents():
    class EmptyRetrievalService:
        def search(self, question: str, top_k: int = 5,allowed_access_levels=None,):
            return []

    llm_provider = FakeLLMProvider()
    generation_service = GenerationService(llm_provider)

    service = RAGService(
        retrieval_service=EmptyRetrievalService(),
        generation_service=generation_service,
    )

    result = service.ask(
        question="What is the company's travel policy?",
        top_k=3,
        
    )

    assert result["question"] == (
        "What is the company's travel policy?"
    )

    assert result["sources"] == []

    assert "don't have enough information" in result["answer"]

    # The LLM must not be called when there is no context.
    assert llm_provider.prompts == []




def test_rag_passes_access_levels_to_retrieval():
    retrieval_service = FakeRetrievalService()

    llm_provider = FakeLLMProvider()
    generation_service = GenerationService(llm_provider)

    service = RAGService(
        retrieval_service=retrieval_service,
        generation_service=generation_service,
    )

    service.ask(
        question="How many annual leave days are provided?",
        allowed_access_levels=["public", "hr"],
    )

    assert retrieval_service.received_access_levels == [
        "public",
        "hr",
    ]