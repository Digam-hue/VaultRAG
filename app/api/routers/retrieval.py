import logging
import os
from functools import lru_cache
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, field_validator

from app.embeddings.huggingface_provider import (
    HuggingFaceEmbeddingProvider,
)
from app.services.embedding_service import EmbeddingService
from app.services.retrieval_service import RetrievalService
from app.vectorstore.chroma_store import ChromaVectorStore

router = APIRouter(prefix="/retrieval", tags=["Retrieval"])
logger = logging.getLogger(__name__)


class SearchRequest(BaseModel):
    question: str = Field(min_length=1, max_length=10_000)
    top_k: int = Field(default=5, ge=1, le=20)

    @field_validator("question")
    @classmethod
    def validate_question(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Question cannot be blank")
        return value


class RetrievedChunk(BaseModel):
    page_content: str
    metadata: dict
    distance: float


class SearchResponse(BaseModel):
    question: str
    result_count: int
    results: list[RetrievedChunk]


@lru_cache(maxsize=1)
def get_retrieval_service() -> RetrievalService:
    provider = HuggingFaceEmbeddingProvider()
    embedding_service = EmbeddingService(provider)

    persist_directory = Path(
        os.getenv("VECTOR_STORE_DIR", "data/chroma")
    )

    vector_store = ChromaVectorStore(
        persist_directory=persist_directory,
    )

    return RetrievalService(
        embedding_service=embedding_service,
        vector_store=vector_store,
    )


@router.post("/search", response_model=SearchResponse)
def search_documents(
    request: SearchRequest,
    service: RetrievalService = Depends(get_retrieval_service),
) -> SearchResponse:
    try:
        results = service.search(
            question=request.question,
            top_k=request.top_k,
        )

        return SearchResponse(
            question=request.question,
            result_count=len(results),
            results=results,
        )

    except Exception as exc:
        logger.exception("Document retrieval failed")
        raise HTTPException(
            status_code=502,
            detail="Document retrieval failed. Check server logs.",
        ) from exc