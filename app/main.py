from fastapi import FastAPI
from app.api.routers.embeddings import router as embeddings_router
from app.api.routers.retrieval import router as retrieval_router
from app.api.routers.ingestion import router as ingestion_router
from app.api.routers.rag import router as rag_router

app = FastAPI(title="VaultRAG")
app.include_router(embeddings_router)
app.include_router(retrieval_router)
app.include_router(ingestion_router)
app.include_router(rag_router)


@app.get("/health")
def health_check():
    return {"status": "ok"}