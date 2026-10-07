from fastapi.testclient import TestClient

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


app.dependency_overrides[get_rag_service] = lambda: FakeRAGService()

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

    assert "30 days of annual leave." in data["answer"]
    

    assert len(data["sources"]) == 1


def test_rag_endpoint_rejects_blank_question():
    response = client.post(
        "/rag/ask",
        json={
            "question": "",
            "top_k": 3,
        },
    )

    assert response.status_code == 422