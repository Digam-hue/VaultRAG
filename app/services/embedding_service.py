import math
from collections.abc import Sequence

from app.core.config import EmbeddingConfig
from app.embeddings.base import EmbeddingProvider, EmbeddingVector
from app.ingestion.models import Document


class EmbeddingService:
    def __init__(
        self,
        provider: EmbeddingProvider,
        config: EmbeddingConfig | None = None,) -> None:
        
        self.provider = provider
        self.config = config or EmbeddingConfig()

    def embed_documents(
        self,
        documents: Sequence[Document],) -> list[EmbeddingVector]:
        
        if not documents:
            return []

        texts = [document.page_content for document in documents]

        if any(not text.strip() for text in texts):
            raise ValueError("Document text cannot be empty")

        vectors: list[EmbeddingVector] = []

        for start in range(0, len(texts), self.config.batch_size):
            batch = texts[start : start + self.config.batch_size]
            batch_vectors = self.provider.embed_documents(batch)

            if len(batch_vectors) != len(batch):
                raise ValueError(
                    "Provider returned a different number of vectors "
                    "than the number of input texts"
                )

            vectors.extend(
                self._validate_vectors(batch_vectors)
            )

        dimensions = {len(vector) for vector in vectors}
        if len(dimensions) != 1:
            raise ValueError(
                "All document embeddings must have equal dimensions"
            )

        return vectors

    def embed_query(self, text: str) -> EmbeddingVector:
        if not text.strip():
            raise ValueError("Query text cannot be empty")

        vector = self.provider.embed_query(text)
        validated = self._validate_vectors([vector])[0]
        return validated

    def _validate_vectors(
        self,
        vectors: Sequence[Sequence[float]],
    ) -> list[EmbeddingVector]:
        if not vectors:
            raise ValueError("Provider returned no vectors")

        validated: list[EmbeddingVector] = []
        expected = self.config.expected_dimensions

        for vector in vectors:
            if not isinstance(vector, (list, tuple)) or not vector:
                raise ValueError("Each embedding must be a non-empty list")

            if expected is not None and len(vector) != expected:
                raise ValueError(
                    f"Expected {expected} dimensions, got {len(vector)}"
                )

            values: EmbeddingVector = []

            for value in vector:
                if isinstance(value, bool) or not isinstance(value, (int, float)):
                    raise ValueError("Embedding values must be numeric")

                number = float(value)

                if not math.isfinite(number):
                    raise ValueError("Embedding values must be finite")

                values.append(number)

            validated.append(values)

        dimensions = {len(vector) for vector in validated}
        if len(dimensions) != 1:
            raise ValueError("Vectors in the same batch must have equal dimensions")

        return validated