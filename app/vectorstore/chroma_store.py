
from pathlib import Path
from collections.abc import Sequence

import chromadb

from app.embeddings.base import EmbeddingVector
from app.ingestion.models import Document


class ChromaVectorStore:
    """Persistent vector storage using externally generated embeddings."""

    def __init__(
        self,
        persist_directory: Path,
        collection_name: str = "vaultrag_chunks",
    ) -> None:
        persist_directory.mkdir(parents=True, exist_ok=True)

        self.client = chromadb.PersistentClient(
            path=str(persist_directory.resolve())
        )

        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},
            embedding_function=None,
        )

    def add_documents(
        self,
        documents: Sequence[Document],
        embeddings: Sequence[EmbeddingVector],
    ) -> None:
        if len(documents) != len(embeddings):
            raise ValueError(
                "The number of documents must match the number of embeddings"
            )

        if not documents:
            return

        ids: list[str] = []
        texts: list[str] = []
        metadatas: list[dict] = []
        vectors: list[list[float]] = []

        for document, embedding in zip(documents, embeddings):
            metadata = document.metadata

            if not embedding:
                raise ValueError("Embedding vectors cannot be empty")

            document_id = metadata.get("document_id")
            chunk_id = metadata.get("chunk_id")

            if document_id is None or chunk_id is None:
                raise ValueError(
                    "Each document must have document_id and chunk_id metadata"
                )

            ids.append(f"{document_id}:{chunk_id}")
            texts.append(document.page_content)

            # Chroma metadata supports primitive values, not arbitrary objects.
            clean_metadata = {}
            for key, value in metadata.items():
                if isinstance(value, (str, int, float, bool)):
                    clean_metadata[key] = value
                elif value is not None:
                    raise ValueError(
                        f"Unsupported metadata value for key: {key}"
                    )

            metadatas.append(clean_metadata)
            vectors.append([float(value) for value in embedding])

        dimensions = {len(vector) for vector in vectors}
        if len(dimensions) != 1:
            raise ValueError(
                "All embeddings must have the same dimensions"
            )

        self.collection.upsert(
            ids=ids,
            documents=texts,
            metadatas=metadatas,
            embeddings=vectors,
        )
    def delete_document(self, document_id: str) -> None:
        """Delete all indexed chunks belonging to one document."""

        if not document_id:
            raise ValueError("document_id cannot be empty")

        self.collection.delete(
            where={"document_id": document_id}
        )
        
    def similarity_search(
        self,
        query_embedding: EmbeddingVector,
        top_k: int = 5,
    ) -> list[dict]:
        if not query_embedding:
            raise ValueError("Query embedding cannot be empty")

        if top_k <= 0:
            raise ValueError("top_k must be greater than zero")

        if self.collection.count() == 0:
            return []

        result = self.collection.query(
            query_embeddings=[[float(value) for value in query_embedding]],
            n_results=min(top_k, self.collection.count()),
            include=["documents", "metadatas", "distances"],
        )

        matches = []

        for i, text in enumerate(result["documents"][0]):
            matches.append(
                {
                    "page_content": text,
                    "metadata": result["metadatas"][0][i],
                    "distance": result["distances"][0][i],
                }
            )

        return matches