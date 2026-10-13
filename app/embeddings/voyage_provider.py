
import os
from collections.abc import Sequence
from typing import Any

import httpx

from app.embeddings.base import EmbeddingVector


class VoyageEmbeddingProvider:
    """Generate retrieval embeddings using Voyage AI."""

    API_URL = "https://api.voyageai.com/v1/embeddings"

    def __init__(
        self,
        model: str | None = None,
        api_key: str | None = None,
    ) -> None:
        token = api_key or os.getenv("VOYAGE_API_KEY")

        if not token:
            raise ValueError(
                "VOYAGE_API_KEY is missing. Add it to your .env file."
            )

        self.model = model or os.getenv(
            "VOYAGE_EMBEDDING_MODEL",
            "voyage-4-lite",
        )
        self.api_key = token

    def _embed(
        self,
        texts: list[str],
        input_type: str,
    ) -> list[EmbeddingVector]:
        if not texts:
            return []

        response = httpx.post(
            self.API_URL,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json={
                "input": texts,
                "model": self.model,
                "input_type": input_type,
                "output_dtype": "float",
            },
            timeout=60.0,
        )

        # Preserve provider failures as upstream errors.
        response.raise_for_status()
        payload: Any = response.json()

        data = payload.get("data") if isinstance(payload, dict) else None

        if not isinstance(data, list) or len(data) != len(texts):
            raise RuntimeError(
                "Voyage returned an invalid number of embeddings."
            )

        data = sorted(data, key=lambda item: item.get("index", -1))

        vectors: list[EmbeddingVector] = []

        for item in data:
            embedding = item.get("embedding")

            if (
                not isinstance(embedding, list)
                or not embedding
                or not all(
                    isinstance(value, (int, float))
                    and not isinstance(value, bool)
                    for value in embedding
                )
            ):
                raise RuntimeError(
                    "Voyage returned an invalid embedding vector."
                )

            vectors.append([float(value) for value in embedding])

        dimensions = len(vectors[0])

        if any(len(vector) != dimensions for vector in vectors):
            raise RuntimeError(
                "Voyage returned embeddings with inconsistent dimensions."
            )

        return vectors

    def embed_documents(
        self,
        texts: Sequence[str],
    ) -> list[EmbeddingVector]:
        return self._embed(list(texts), input_type="document")

    def embed_query(self, text: str) -> EmbeddingVector:
        if not text.strip():
            raise ValueError("Query text cannot be empty")

        vectors = self._embed([text], input_type="query")
        return vectors[0]
