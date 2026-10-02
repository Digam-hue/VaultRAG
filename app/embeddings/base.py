
from typing import Protocol, Sequence


EmbeddingVector = list[float]


class EmbeddingProvider(Protocol):
    """Contract for any document/query embedding provider."""

    def embed_documents(
        self,
        texts: Sequence[str],) -> list[EmbeddingVector]:
        """Convert multiple document texts into vectors."""
        ...
        ###... is ellipsis,means: There is no implementation here; this is only a contract for any providers,openai,claude,hf,ollama."

    def embed_query(self, text: str) -> EmbeddingVector:
        """Convert one search query into a vector."""
        ...