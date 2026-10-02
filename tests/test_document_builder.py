from app.ingestion.document_builder import create_documents

def test_create_documents():
    chunks = [
        "Employee Leave Policy",
        "Employees receive 20 days.",
    ]

    documents = create_documents(
        chunks=chunks,
        source="data/documents/leave_policy.txt",
    )

    assert len(documents) == 2

    assert documents[0].page_content == "Employee Leave Policy"
    assert documents[0].metadata["source"] == "leave_policy.txt"
    assert documents[0].metadata["chunk_id"] == 0

    assert documents[1].metadata["chunk_id"] == 1
    
    
def test_empty_chunks_are_skipped():
    chunks = [
        "First chunk",
        "",
        "   ",
        "Second chunk",
    ]

    documents = create_documents(
        chunks=chunks,
        source="test.txt",
    )

    assert len(documents) == 2
    assert documents[0].metadata["chunk_id"] == 0
    assert documents[1].metadata["chunk_id"] == 1