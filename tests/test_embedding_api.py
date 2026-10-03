
from fastapi.testclient import TestClient

from app.main import app
from app.api.routers.embeddings import get_embedding_service


class FakeEmbeddingProvider:
    """Deterministic provider for API tests only."""

    model = "test-embedding-model"

    def embed_query(self, text: str) -> list[float]:
        return [0.1, 0.2, 0.3]

    def embed_documents(self, texts):
        return [[0.1, 0.2, 0.3] for _ in texts]


client = TestClient(app)


def setup_function():
    app.dependency_overrides.clear()


def teardown_function():
    app.dependency_overrides.clear()


def test_query_embedding_success():
    from app.services.embedding_service import EmbeddingService

    app.dependency_overrides[get_embedding_service] = (
        lambda: EmbeddingService(FakeEmbeddingProvider())
    )

    response = client.post(
        "/embeddings/query",
        json={"text": "How does semantic search work?"},
    )

    assert response.status_code == 200

    data = response.json()
    assert data["model"] == "test-embedding-model"
    assert data["dimensions"] == 3
    assert data["embedding"] == [0.1, 0.2, 0.3]


def test_query_embedding_rejects_empty_text():
    response = client.post(
        "/embeddings/query",
        json={"text": ""},
    )

    assert response.status_code == 422


def test_query_embedding_rejects_missing_text():
    response = client.post(
        "/embeddings/query",
        json={},
    )

    assert response.status_code == 422


def test_query_embedding_rejects_blank_text():
    response = client.post(
        "/embeddings/query",
        json={"text": "   "},
    )

    assert response.status_code == 422