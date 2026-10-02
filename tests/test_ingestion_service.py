
import pytest

from app.core.config import IngestionConfig
from app.services.ingestion_service import IngestionService


def test_ingest_file_end_to_end(tmp_path):
    documents_dir = tmp_path / "documents"
    documents_dir.mkdir()

    source = documents_dir / "leave_policy.txt"
    source.write_text(
        "Employees receive annual leave. "
        "Managers approve leave requests.",
        encoding="utf-8",
    )

    service = IngestionService(
        documents_dir=documents_dir,
        config=IngestionConfig(
            chunk_size=30,
            chunk_overlap=5,
        ),
    )

    documents = service.ingest_file(source)

    assert len(documents) > 1

    first = documents[0]

    assert first.page_content
    assert first.metadata["source"] == "leave_policy.txt"
    assert first.metadata["document_id"]
    assert first.metadata["content_hash"]
    assert first.metadata["chunk_id"] == 0
    assert first.metadata["chunk_count"] == len(documents)

    assert all(
        doc.metadata["document_id"]
        == first.metadata["document_id"]
        for doc in documents
    )


def test_content_hash_changes_when_file_changes(tmp_path):
    documents_dir = tmp_path / "documents"
    documents_dir.mkdir()

    source = documents_dir / "policy.txt"
    source.write_text("Original policy text", encoding="utf-8")

    service = IngestionService(documents_dir=documents_dir)
    original = service.ingest_file(source)

    source.write_text("Updated policy text", encoding="utf-8")
    updated = service.ingest_file(source)

    assert (
        original[0].metadata["document_id"]
        == updated[0].metadata["document_id"]
    )
    assert (
        original[0].metadata["content_hash"]
        != updated[0].metadata["content_hash"]
    )


def test_reject_file_outside_documents_directory(tmp_path):
    documents_dir = tmp_path / "documents"
    documents_dir.mkdir()

    outside_file = tmp_path / "secret.txt"
    outside_file.write_text("Private text", encoding="utf-8")

    service = IngestionService(documents_dir=documents_dir)

    with pytest.raises(ValueError, match="inside the documents directory"):
        service.ingest_file(outside_file)


def test_reject_empty_document(tmp_path):
    documents_dir = tmp_path / "documents"
    documents_dir.mkdir()

    source = documents_dir / "empty.txt"
    source.write_text("   \n", encoding="utf-8")

    service = IngestionService(documents_dir=documents_dir)

    with pytest.raises(ValueError, match="empty"):
        service.ingest_file(source)


def test_reject_unsupported_file_type(tmp_path):
    documents_dir = tmp_path / "documents"
    documents_dir.mkdir()

    source = documents_dir / "policy.pdf"
    source.write_text("Not really a PDF", encoding="utf-8")

    service = IngestionService(documents_dir=documents_dir)

    with pytest.raises(ValueError, match="Only .txt files"):
        service.ingest_file(source)