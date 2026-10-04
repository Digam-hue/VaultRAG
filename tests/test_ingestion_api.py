
from fastapi.testclient import TestClient

from app.main import app
from app.api.routers.ingestion import get_indexing_service


class FakeIndexingService:
    def index_file(self, file_path):
        return {
            "source": file_path.name,
            "document_id": "test-doc-1",
            "chunks_indexed": 3,
        }


client = TestClient(app)


def setup_function():
    app.dependency_overrides.clear()


def teardown_function():
    app.dependency_overrides.clear()


def test_index_endpoint_success():
    app.dependency_overrides[get_indexing_service] = (
        lambda: FakeIndexingService()
    )

    response = client.post(
        "/ingestion/index",
        json={"filename": "handbook.txt"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["source"] == "handbook.txt"
    assert data["document_id"] == "test-doc-1"
    assert data["chunks_indexed"] == 3


def test_index_endpoint_rejects_directory_path():
    response = client.post(
        "/ingestion/index",
        json={"filename": "../secret.txt"},
    )

    assert response.status_code == 400


def test_index_endpoint_rejects_missing_filename():
    response = client.post(
        "/ingestion/index",
        json={},
    )

    assert response.status_code == 422