
import hashlib
from pathlib import Path

from app.core.config import IngestionConfig
from app.ingestion.chunker import chunk_text
from app.ingestion.document_builder import (
    create_documents,
    sha256_text,
)
from app.ingestion.loader import load_text_file
from app.ingestion.models import Document


class IngestionService:
    def __init__(
        self,
        documents_dir: Path,
        config: IngestionConfig | None = None,) -> None:
        
        self.documents_dir = documents_dir.resolve()
        self.config = config or IngestionConfig()

    def ingest_file(self, file_path: Path) -> list[Document]:
        path = file_path.resolve()

        # Prevent paths outside the configured knowledge directory.
        if not path.is_relative_to(self.documents_dir):
            raise ValueError(
                "File must be inside the documents directory"
            )

        if not path.is_file():
            raise FileNotFoundError(f"Document not found: {path.name}")

        if path.suffix.lower() != ".txt":
            raise ValueError("Only .txt files are supported currently")

        text = load_text_file(str(path))

        if not text.strip():
            raise ValueError("Document is empty")

        source_key = path.relative_to(self.documents_dir).as_posix()

        document_id = hashlib.sha256(
            source_key.encode("utf-8")# here source_key is not str it is a path 
        ).hexdigest()

        content_hash = sha256_text(text)

        chunks = chunk_text(
            text=text,
            chunk_size=self.config.chunk_size,
            overlap=self.config.chunk_overlap,
        )

        return create_documents(
            chunks=chunks,
            source=source_key,
            document_id=document_id,
            content_hash=content_hash,
        )