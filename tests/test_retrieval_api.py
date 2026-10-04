
from fastapi.testclient import TestClient

from app.main import app
from app.api.routers.retrieval import get_retrieval_service


class FakeRetrievalService:
    def search(self, question, top_k=5):
        return [
            {
                "page_content": "Employees receive 20 days of annual leave.",
                "metadata": {"source": "handbook.txt"},
                "distance": 0.08,
            }
        ]


client = TestClient(app)


def setup_function():
    app.dependency_overrides.clear()


def teardown_function():
    app.dependency_overrides.clear()


def test_search_endpoint_success():
    app.dependency_overrides[get_retrieval_service] = (
        lambda: FakeRetrievalService()
    )

    response = client.post(
        "/retrieval/search",
        json={
            "question": "What is the leave policy?",
            "top_k": 3,
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert data["result_count"] == 1
    assert data["results"][0]["metadata"]["source"] == "handbook.txt"
    assert "20 days" in data["results"][0]["page_content"]


def test_search_endpoint_rejects_blank_question():
    response = client.post(
        "/retrieval/search",
        json={"question": "   ", "top_k": 3},
    )

    assert response.status_code == 422


def test_search_endpoint_rejects_invalid_top_k():
    response = client.post(
        "/retrieval/search",
        json={"question": "What is the leave policy?", "top_k": 0},
    )

    assert response.status_code == 422


def test_search_endpoint_rejects_missing_question():
    response = client.post(
        "/retrieval/search",
        json={"top_k": 3},
    )

    assert response.status_code == 422