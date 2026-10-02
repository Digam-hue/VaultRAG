from app.ingestion.models import Document


def test_document_creation():
    document = Document(
        page_content="Employee Leave Policy",
        metadata={"source": "leave_policy.txt"},
        
    )

    assert document.page_content == "Employee Leave Policy"
    assert document.metadata["source"] == "leave_policy.txt"


def test_document_has_independent_metadata():
    document_1 = Document(page_content="Document 1")
    document_2 = Document(page_content="Document 2")

    document_1.metadata["source"] = "file1.txt"

    assert document_2.metadata == {}