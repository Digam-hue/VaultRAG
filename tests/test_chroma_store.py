from pathlib import Path

from app.ingestion.models import Document
from app.vectorstore.chroma_store import ChromaVectorStore


def test_similarity_search_filters_by_access_level(tmp_path: Path):
    store = ChromaVectorStore(
        persist_directory=tmp_path,
        collection_name="test_permissions",
    )

    documents = [
        Document(
            page_content="Public workplace policy",
            metadata={
                "source": "public.txt",
                "document_id": "public-doc",
                "chunk_id": 0,
                "access_level": "public",
            },
        ),
        Document(
            page_content="Confidential HR salary policy",
            metadata={
                "source": "hr.txt",
                "document_id": "hr-doc",
                "chunk_id": 0,
                "access_level": "hr",
            },
        ),
        Document(
            page_content="Confidential management strategy",
            metadata={
                "source": "manager.txt",
                "document_id": "manager-doc",
                "chunk_id": 0,
                "access_level": "manager",
            },
        ),
    ]

    embeddings = [
        [1.0, 0.0, 0.0],
        [0.99, 0.01, 0.0],
        [0.98, 0.02, 0.0],
    ]

    store.add_documents(
        documents=documents,
        embeddings=embeddings,
    )

    results = store.similarity_search(
        query_embedding=[1.0, 0.0, 0.0],
        top_k=10,
        allowed_access_levels=["public", "hr"],
    )

    access_levels = {
        result["metadata"]["access_level"]
        for result in results
    }

    assert access_levels == {"public", "hr"}
    assert "manager" not in access_levels