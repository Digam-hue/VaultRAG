
import pytest

from app.services.retrieval_service import RetrievalService


class FakeEmbeddingService:
    def __init__(self):
        self.received_questions = []
        

    def embed_query(self, question):
        self.received_questions.append(question)
        return [0.9, 0.1, 0.0]


class FakeVectorStore:
    def __init__(self):
        self.received_embedding = None
        self.received_top_k = None
        self.received_access_levels = None

    def similarity_search(
            self, 
            query_embedding, 
            top_k=5,
            allowed_access_levels=None,
        ):
        
        self.received_embedding = query_embedding
        self.received_top_k = top_k
        self.received_access_levels = allowed_access_levels

        return [
            {
                "page_content": "Employees receive 20 days of annual leave.",
                "metadata": {"source": "handbook.txt"},
                "distance": 0.08,
            }
        ]


def test_search_embeds_question_and_retrieves_chunks():
    embedding_service = FakeEmbeddingService()
    vector_store = FakeVectorStore()

    service = RetrievalService(embedding_service, vector_store)

    results = service.search("What is the leave policy?", top_k=3)

    assert embedding_service.received_questions == [
        "What is the leave policy?"
    ]
    assert vector_store.received_embedding == [0.9, 0.1, 0.0]
    assert vector_store.received_top_k == 3
    assert len(results) == 1
    assert "20 days" in results[0]["page_content"]


def test_search_rejects_blank_question():
    service = RetrievalService(
        FakeEmbeddingService(),
        FakeVectorStore(),
    )

    with pytest.raises(ValueError, match="Question cannot be empty"):
        service.search("   ")


def test_search_rejects_invalid_top_k():
    service = RetrievalService(
        FakeEmbeddingService(),
        FakeVectorStore(),
    )

    with pytest.raises(ValueError, match="top_k"):
        service.search("What is the leave policy?", top_k=0)
        

def test_search_passes_allowed_access_levels_to_vector_store():
    embedding_service = FakeEmbeddingService()
    vector_store = FakeVectorStore()

    service = RetrievalService(
        embedding_service,
        vector_store,
    )

    service.search(
        "What is the HR leave policy?",
        top_k=3,
        allowed_access_levels=["public", "hr"],
    )

    assert vector_store.received_access_levels == [
        "public",
        "hr",
    ]