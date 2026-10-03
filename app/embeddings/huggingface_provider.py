'''
It will use Hugging Face's hosted inference client, accept batches of text,
convert provider responses into ordinary Python vectors, and 
raise useful errors if the provider is unavailable or the response is invalid.
'''

import os
from collections.abc import Sequence
from typing import Any

from huggingface_hub import InferenceClient

from app.embeddings.base import EmbeddingVector


class HuggingFaceEmbeddingProvider:
    """Generate embeddings through Hugging Face hosted inference."""

    def __init__(
        self,
        model: str | None = None,
        api_key: str | None = None,
    ) -> None:
        token = api_key or os.getenv("HF_TOKEN")

        if not token:
            raise ValueError(
                "HF_TOKEN is missing. Add it to your local .env file."
            )

        self.model = model or os.getenv(
            "HF_EMBEDDING_MODEL",
            "BAAI/bge-small-en-v1.5",
        )

        self.client = InferenceClient(
            model=self.model,
            api_key=token,
            provider="auto",
        )

    def embed_documents(
        self,
        texts: Sequence[str],
    ) -> list[EmbeddingVector]:
        if not texts:
            return []

        result = self.client.feature_extraction(
            text=list(texts),
        )

        vectors = self._convert_result(result)

        if len(vectors) != len(texts):
            raise ValueError(
                f"Expected {len(texts)} embeddings, "
                f"received {len(vectors)}."
            )

        return vectors

    def embed_query(self, text: str) -> EmbeddingVector:
        if not text.strip():
            raise ValueError("Query text cannot be empty")

        result = self.client.feature_extraction(text=text)
        vectors = self._convert_result(result)

        if len(vectors) != 1:
            raise ValueError(
                f"Expected one query embedding, received {len(vectors)}."
            )

        return vectors[0]

    @staticmethod
    def _convert_result(result: Any) -> list[EmbeddingVector]:
        # Hugging Face commonly returns a NumPy array.
        if hasattr(result, "tolist"):
            result = result.tolist()

        if not isinstance(result, (list, tuple)) or not result:
            raise ValueError(
                "Hugging Face returned an empty or invalid embedding result."
            )

        # A single text may be returned as either [dimensions]
        # or [[dimensions]]. Normalize both to [[dimensions]].
        if isinstance(result[0], (int, float)):
            result = [result]

        vectors: list[EmbeddingVector] = []

        for vector in result:
            if not isinstance(vector, (list, tuple)) or not vector:
                raise ValueError("Invalid embedding vector returned.")

            vectors.append(list(vector))

        return vectors
