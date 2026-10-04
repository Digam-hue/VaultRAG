
import pytest

from app.ingestion.models import Document
from app.vectorstore.chroma_store import ChromaVectorStore


def make_document(text, document_id, chunk_id):
    
    return Document(
        page_content=text,
        metadata={
            "source": "handbook.txt",
            "document_id": document_id,
            "content_hash": "test-hash",
            "chunk_id": chunk_id,
            "chunk_count": 2,
        },
    )


def test_add_and_search_documents(tmp_path):
    store = ChromaVectorStore(
        persist_directory=tmp_path / "vectors",
        collection_name="test_collection",
    )

    documents = [
        make_document("The leave policy allows 20 days.", "doc1", 0),
        make_document("Python is a programming language.", "doc2", 0),
    ]

    embeddings = [
        [1.0, 0.0, 0.0],
        [0.0, 1.0, 0.0],
    ]

    store.add_documents(documents, embeddings)

    results = store.similarity_search(
        query_embedding=[0.99, 0.01, 0.0],
        top_k=1,
    )

    assert len(results) == 1
    assert "leave policy" in results[0]["page_content"]
    assert results[0]["metadata"]["document_id"] == "doc1"


def test_rejects_mismatched_document_and_embedding_counts(tmp_path):
    store = ChromaVectorStore(
        persist_directory=tmp_path / "vectors",
        collection_name="mismatch_collection",
    )

    documents = [make_document("Some text", "doc1", 0)]

    with pytest.raises(ValueError, match="must match"):
        store.add_documents(documents, [])


def test_empty_store_returns_no_results(tmp_path):
    store = ChromaVectorStore(
        persist_directory=tmp_path / "vectors",
        collection_name="empty_collection",
    )

    assert store.similarity_search([1.0, 0.0, 0.0]) == []


def test_rejects_invalid_top_k(tmp_path):
    store = ChromaVectorStore(
        persist_directory=tmp_path / "vectors",
        collection_name="top_k_collection",
    )

    with pytest.raises(ValueError, match="top_k"):
        store.similarity_search([1.0, 0.0, 0.0], top_k=0)