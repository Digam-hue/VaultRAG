
import pytest

from app.core.config import EmbeddingConfig
from app.services.embedding_service import EmbeddingService
from app.ingestion.models import Document


class FakeEmbeddingProvider:
    """Deterministic provider for unit tests only."""

    def __init__(self):
        self.document_batches = []

    def embed_documents(self, texts):
        self.document_batches.append(list(texts))
        return [[float(len(text)), 1.0, 2.0] for text in texts]

    def embed_query(self, text):
        return [float(len(text)), 1.0, 2.0]


def make_document(text: str) -> Document:
    return Document(page_content=text, metadata={})


def test_embeds_documents():
    provider = FakeEmbeddingProvider()
    service = EmbeddingService(provider)

    vectors = service.embed_documents([
        make_document("hello"),
        make_document("vault rag"),
    ])

    assert len(vectors) == 2
    assert vectors[0] == [5.0, 1.0, 2.0]
    assert vectors[1] == [9.0, 1.0, 2.0]


def test_batches_documents():
    provider = FakeEmbeddingProvider()
    service = EmbeddingService(
        provider,
        EmbeddingConfig(batch_size=2),
    )

    documents = [make_document(f"text {i}") for i in range(5)]
    vectors = service.embed_documents(documents)

    assert len(vectors) == 5
    assert [len(batch) for batch in provider.document_batches] == [2, 2, 1]


def test_empty_document_list_returns_empty_list():
    service = EmbeddingService(FakeEmbeddingProvider())

    assert service.embed_documents([]) == []


def test_rejects_blank_query():
    service = EmbeddingService(FakeEmbeddingProvider())

    with pytest.raises(ValueError, match="Query text cannot be empty"):
        service.embed_query("   ")


def test_rejects_wrong_vector_dimensions():
    service = EmbeddingService(
        FakeEmbeddingProvider(),
        EmbeddingConfig(expected_dimensions=4),
    )

    with pytest.raises(ValueError, match="Expected 4 dimensions"):
        service.embed_query("hello")


def test_rejects_non_finite_values():
    class InvalidProvider(FakeEmbeddingProvider):
        def embed_query(self, text):
            return [float("nan"), 1.0]

    service = EmbeddingService(InvalidProvider())

    with pytest.raises(ValueError, match="must be finite"):
        service.embed_query("hello")


def test_rejects_wrong_number_of_vectors():
    class WrongCountProvider(FakeEmbeddingProvider):
        def embed_documents(self, texts):
            return []

    service = EmbeddingService(WrongCountProvider())

    with pytest.raises(ValueError, match="different number of vectors"):
        service.embed_documents([make_document("hello")])