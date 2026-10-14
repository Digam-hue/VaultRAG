from fastapi.testclient import TestClient
import pytest
from app.main import app
from app.api.routers.rag import get_rag_service


class FakeRAGService:
    def ask(self, question: str, top_k: int = 5):
        return {
            "question": question,
            "answer": "Employees receive 30 days of annual leave.",
            "sources": [
                {
                    "page_content": "Employees receive 30 days of annual leave.",
                    "metadata": {
                        "source": "leave_policy.txt",
                    },
                    "distance": 0.1,
                }
            ],
        }


# app.dependency_overrides[get_rag_service] = lambda: FakeRAGService()


def setup_function():
    app.dependency_overrides[get_rag_service] = (
        lambda: FakeRAGService()
    )


def teardown_function():
    app.dependency_overrides.clear()

client = TestClient(app)


def test_rag_endpoint():
    response = client.post(
        "/rag/ask",
        json={
            "question": "How many annual leave days are provided?",
            "top_k": 3,
        },
    )

    assert response.status_code == 200

    data = response.json()

    # assert "20 days of annual leave" in data["answer"]
    
    print(data["sources"])
    # assert len(data["sources"]) == 1


@pytest.mark.parametrize("top_k", [0, 21])
def test_rag_endpoint_rejects_invalid_top_k(top_k):
    response = client.post(
        "/rag/ask",
        json={
            "question": "What is the leave policy?",
            "top_k": top_k,
        },
    )

    assert response.status_code == 422


def test_rag_endpoint_maps_value_error_to_400():
    class InvalidQuestionService:
        def ask(self, question: str, top_k: int = 5):
            raise ValueError("Question cannot be empty")

    app.dependency_overrides[get_rag_service] = (
        lambda: InvalidQuestionService()
    )

    response = client.post(
        "/rag/ask",
        json={"question": "Valid request"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Question cannot be empty"


def test_rag_endpoint_hides_unexpected_error_details():
    class BrokenRAGService:
        def ask(self, question: str, top_k: int = 5):
            raise RuntimeError("Internal database credentials leaked")

    app.dependency_overrides[get_rag_service] = (
        lambda: BrokenRAGService()
    )

    response = client.post(
        "/rag/ask",
        json={"question": "What is the leave policy?"},
    )

    assert response.status_code == 502

    detail = response.json()["detail"]

    assert detail == (
        "RAG generation failed. Check server logs."
    )
    assert "credentials" not in detail

def test_rag_endpoint_rejects_blank_question():
    response = client.post(
        "/rag/ask",
        json={
            "question": "",
            "top_k": 3,
        },
    )

    assert response.status_code == 422