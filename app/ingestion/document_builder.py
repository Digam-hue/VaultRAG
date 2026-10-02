
import hashlib
from pathlib import Path

from app.ingestion.models import Document


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def create_documents(
    chunks: list[str],
    source: str,
    document_id: str,
    content_hash: str,
) -> list[Document]:
    source_name = Path(source).name
    non_empty_chunks = [
        chunk for chunk in chunks if chunk.strip()
    ]

    return [
        Document(
            page_content=chunk,
            metadata={
                "source": source_name,
                "document_id": document_id,
                "content_hash": content_hash,
                "chunk_id": index,
                "chunk_count": len(non_empty_chunks),
            },
        )
        for index, chunk in enumerate(non_empty_chunks)
    ]