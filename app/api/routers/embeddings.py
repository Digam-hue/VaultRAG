
import logging
from functools import lru_cache

from dotenv import load_dotenv
from fastapi import APIRouter,Depends, HTTPException
from pydantic import BaseModel, Field, field_validator

from app.embeddings.huggingface_provider import (
    HuggingFaceEmbeddingProvider,
)
from app.services.embedding_service import EmbeddingService

load_dotenv()

router = APIRouter(prefix="/embeddings", tags=["Embeddings"])
logger = logging.getLogger(__name__)


class QueryEmbeddingRequest(BaseModel):
    text: str = Field(min_length=1, max_length=10_000)

    @field_validator("text")
    @classmethod
    def validate_text(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Query text cannot be blank")
        return value


class QueryEmbeddingResponse(BaseModel):
    model: str
    dimensions: int
    embedding: list[float]


@lru_cache(maxsize=1)
def get_embedding_service() -> EmbeddingService:
    provider = HuggingFaceEmbeddingProvider()
    return EmbeddingService(provider)


@router.post(
    "/query",
    response_model=QueryEmbeddingResponse,
)
def create_query_embedding(
    request: QueryEmbeddingRequest,
    service: EmbeddingService = Depends(get_embedding_service),
) -> QueryEmbeddingResponse:
    try:
        
        vector = service.embed_query(request.text)

        return QueryEmbeddingResponse(
            model=service.provider.model,
            dimensions=len(vector),
            embedding=vector,
        )

    except Exception as exc:
        logger.exception("Embedding provider request failed")
        raise HTTPException(
            status_code=502,
            detail="Embedding provider request failed. Check server logs.",
        ) from exc