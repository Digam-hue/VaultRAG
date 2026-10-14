
from types import SimpleNamespace

import pytest

from app.llm.groq_provider import GroqLLMProvider
from app.embeddings.voyage_provider import VoyageEmbeddingProvider


# ---------------- GROQ PROVIDER ----------------

def test_groq_requires_api_key(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)

    with pytest.raises(ValueError, match="GROQ_API_KEY"):
        GroqLLMProvider()


def test_groq_generates_answer(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    monkeypatch.setenv("GROQ_MODEL", "openai/gpt-oss-120b")

    class FakeGroq:
        def __init__(self, api_key):
            self.api_key = api_key
            self.chat = SimpleNamespace(
                completions=SimpleNamespace(create=self.create)
            )

        def create(self, **kwargs):
            assert kwargs["model"] == "openai/gpt-oss-120b"
            assert kwargs["temperature"] == 0
            assert kwargs["messages"][0]["content"] == "Test prompt"

            return SimpleNamespace(
                choices=[
                    SimpleNamespace(
                        message=SimpleNamespace(content="  Test answer  ")
                    )
                ]
            )

    monkeypatch.setattr("app.llm.groq_provider.Groq", FakeGroq)

    provider = GroqLLMProvider()

    assert provider.generate("Test prompt") == "Test answer"


def test_groq_rejects_blank_prompt(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "test-key")

    class FakeGroq:
        def __init__(self, api_key):
            pass

    monkeypatch.setattr("app.llm.groq_provider.Groq", FakeGroq)

    provider = GroqLLMProvider()

    with pytest.raises(ValueError, match="Prompt cannot be empty"):
        provider.generate("   ")


def test_groq_rejects_empty_response(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "test-key")

    class FakeGroq:
        def __init__(self, api_key):
            self.chat = SimpleNamespace(
                completions=SimpleNamespace(
                    create=lambda **kwargs: SimpleNamespace(
                        choices=[
                            SimpleNamespace(
                                message=SimpleNamespace(content=None)
                            )
                        ]
                    )
                )
            )

    monkeypatch.setattr("app.llm.groq_provider.Groq", FakeGroq)

    provider = GroqLLMProvider()

    with pytest.raises(ValueError, match="empty response"):
        provider.generate("Test prompt")


# ---------------- VOYAGE PROVIDER ----------------

def test_voyage_requires_api_key(monkeypatch):
    monkeypatch.delenv("VOYAGE_API_KEY", raising=False)

    with pytest.raises(ValueError, match="VOYAGE_API_KEY"):
        VoyageEmbeddingProvider()


def test_voyage_returns_document_embeddings(monkeypatch):
    monkeypatch.setenv("VOYAGE_API_KEY", "test-key")

    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            # Deliberately reverse the indices to test ordering.
            return {
                "data": [
                    {"index": 1, "embedding": [0.4, 0.5]},
                    {"index": 0, "embedding": [0.1, 0.2]},
                ]
            }

    def fake_post(url, **kwargs):
        assert url == VoyageEmbeddingProvider.API_URL
        assert kwargs["headers"]["Authorization"] == "Bearer test-key"
        assert kwargs["json"]["input"] == ["first", "second"]
        assert kwargs["json"]["input_type"] == "document"
        return FakeResponse()

    monkeypatch.setattr("app.embeddings.voyage_provider.httpx.post", fake_post)

    provider = VoyageEmbeddingProvider()

    assert provider.embed_documents(["first", "second"]) == [
        [0.1, 0.2],
        [0.4, 0.5],
    ]


def test_voyage_returns_query_embedding(monkeypatch):
    monkeypatch.setenv("VOYAGE_API_KEY", "test-key")

    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {
                "data": [{"index": 0, "embedding": [0.1, 0.2, 0.3]}]
            }

    monkeypatch.setattr(
        "app.embeddings.voyage_provider.httpx.post",
        lambda *args, **kwargs: FakeResponse(),
    )

    provider = VoyageEmbeddingProvider()

    assert provider.embed_query("test query") == [0.1, 0.2, 0.3]


def test_voyage_empty_documents_skip_api_call(monkeypatch):
    monkeypatch.setenv("VOYAGE_API_KEY", "test-key")

    def unexpected_call(*args, **kwargs):
        raise AssertionError("API should not be called")

    monkeypatch.setattr(
        "app.embeddings.voyage_provider.httpx.post",
        unexpected_call,
    )

    provider = VoyageEmbeddingProvider()

    assert provider.embed_documents([]) == []


def test_voyage_rejects_blank_query(monkeypatch):
    monkeypatch.setenv("VOYAGE_API_KEY", "test-key")
    provider = VoyageEmbeddingProvider()

    with pytest.raises(ValueError, match="Query text cannot be empty"):
        provider.embed_query("   ")


def test_voyage_rejects_invalid_embedding_count(monkeypatch):
    monkeypatch.setenv("VOYAGE_API_KEY", "test-key")

    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {
                "data": [{"index": 0, "embedding": [0.1, 0.2]}]
            }

    monkeypatch.setattr(
        "app.embeddings.voyage_provider.httpx.post",
        lambda *args, **kwargs: FakeResponse(),
    )

    provider = VoyageEmbeddingProvider()

    with pytest.raises(RuntimeError, match="invalid number"):
        provider.embed_documents(["first", "second"])


def test_voyage_rejects_inconsistent_dimensions(monkeypatch):
    monkeypatch.setenv("VOYAGE_API_KEY", "test-key")

    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {
                "data": [
                    {"index": 0, "embedding": [0.1, 0.2]},
                    {"index": 1, "embedding": [0.3, 0.4, 0.5]},
                ]
            }

    monkeypatch.setattr(
        "app.embeddings.voyage_provider.httpx.post",
        lambda *args, **kwargs: FakeResponse(),
    )

    provider = VoyageEmbeddingProvider()

    with pytest.raises(RuntimeError, match="inconsistent dimensions"):
        provider.embed_documents(["first", "second"])
