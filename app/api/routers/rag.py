import os
from functools import lru_cache
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.embeddings.huggingface_provider import HuggingFaceEmbeddingProvider
from app.llm.groq_provider import GroqLLMProvider
from app.services.embedding_service import EmbeddingService
from app.services.generation_service import GenerationService
from app.services.rag_service import RAGService
from app.services.retrieval_service import RetrievalService
from app.vectorstore.chroma_store import ChromaVectorStore


router = APIRouter(
    prefix="/rag",
    tags=["RAG"],
)


class RAGRequest(BaseModel):
    question: str = Field(min_length=1)
    top_k: int = Field(default=5, ge=1, le=20)


class RAGResponse(BaseModel):
    question: str
    answer: str
    sources: list[dict]


@lru_cache(maxsize=1)
def get_rag_service() -> RAGService:
    vector_directory = Path(
        os.getenv("VECTOR_STORE_DIR", "data/chroma")
    ).resolve()

    embedding_service = EmbeddingService(
        HuggingFaceEmbeddingProvider()
    )

    vector_store = ChromaVectorStore(
        persist_directory=vector_directory
    )

    retrieval_service = RetrievalService(
        embedding_service=embedding_service,
        vector_store=vector_store,
    )

    generation_service = GenerationService(
        llm_provider=GroqLLMProvider()
    )

    return RAGService(
        retrieval_service=retrieval_service,
        generation_service=generation_service,
    )


@router.post("/ask", response_model=RAGResponse)
def ask_question(
    request: RAGRequest,
    service: RAGService = Depends(get_rag_service),
):
    try:
        return service.ask(
            question=request.question,
            top_k=request.top_k,
        )
    except ValueError as exc:
        print(exc)
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        print(exc)
        raise HTTPException(
            status_code=502,
            detail="RAG generation failed. Check server logs.",
        ) from exc