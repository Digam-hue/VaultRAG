from pathlib import Path

from app.ingestion.models import Document


def create_documents(
    chunks: list[str],
    source: str,
) -> list[Document]:
    documents = []

    source_name = Path(source).name

    for chunk in chunks:
        if not chunk.strip():
            continue

        document = Document(
            page_content=chunk,
            metadata={
                "source": source_name,
                "chunk_id": len(documents),
            },
        )

        documents.append(document)

    return documents