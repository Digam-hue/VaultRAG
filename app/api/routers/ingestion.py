
import logging
import os
from functools import lru_cache
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.embeddings.huggingface_provider import (
    HuggingFaceEmbeddingProvider,
)
from app.services.embedding_service import EmbeddingService
from app.services.indexing_service import IndexingService
from app.services.ingestion_service import IngestionService
from app.vectorstore.chroma_store import ChromaVectorStore

router = APIRouter(prefix="/ingestion", tags=["Ingestion"])
logger = logging.getLogger(__name__)


class IndexRequest(BaseModel):
    filename: str = Field(min_length=1, max_length=255)


class IndexResponse(BaseModel):
    source: str
    document_id: str
    chunks_indexed: int


@lru_cache(maxsize=1)
def get_indexing_service() -> IndexingService:
    documents_dir = Path(
        os.getenv("DOCUMENTS_DIR", "data/documents")
    ).resolve()

    vector_directory = Path(
        os.getenv("VECTOR_STORE_DIR", "data/chroma")
    ).resolve()

    ingestion_service = IngestionService(
        documents_dir=documents_dir,
    )

    embedding_service = EmbeddingService(
        HuggingFaceEmbeddingProvider(),
    )

    vector_store = ChromaVectorStore(
        persist_directory=vector_directory,
    )

    return IndexingService(
        ingestion_service=ingestion_service,
        embedding_service=embedding_service,
        vector_store=vector_store,
    )


@router.post("/index", response_model=IndexResponse)
def index_document(
    request: IndexRequest,
    service: IndexingService = Depends(get_indexing_service),
) -> IndexResponse:
    # Accept a filename, not an arbitrary filesystem path.
    if (
        Path(request.filename).name != request.filename
        or request.filename in {".", ".."}
    ):
        raise HTTPException(
            status_code=400,
            detail="Provide a filename only, without directory paths.",
        )

    documents_dir = Path(
        os.getenv("DOCUMENTS_DIR", "data/documents")
    ).resolve()
    file_path = documents_dir / request.filename

    try:
        result = service.index_file(file_path)
        return IndexResponse(**result)

    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail="Document not found in the configured documents directory.",
        ) from exc

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        logger.exception("Document indexing failed")
        raise HTTPException(
            status_code=502,
            detail="Document indexing failed. Check server logs.",
        ) from exc