from collections.abc import Sequence

from app.ingestion.models import Document
from app.llm.base import LLMProvider


class GenerationService:
    """Generate answers grounded in retrieved documents."""

    def __init__(self, llm_provider: LLMProvider) -> None:
        self.llm_provider = llm_provider

    def generate_answer(
        self,
        question: str,
        documents: Sequence[dict],
    ) -> str:
        if not question.strip():
            raise ValueError("Question cannot be empty")

        if not documents:
            return (
                "I don't have enough information in the available "
                "documents to answer that question."
            )

        context_parts = []

        for index, document in enumerate(documents, start=1):
            content = document.get("page_content", "").strip()

            if not content:
                continue

            context_parts.append(
                f"[Source {index}]\n{content}"
            )

        if not context_parts:
            return (
                "I don't have enough information in the available "
                "documents to answer that question."
            )

        context = "\n\n".join(context_parts)

        prompt = f"""You are VaultRAG, an enterprise knowledge assistant.

Answer the user's question using ONLY the provided context.

Rules:
1. Do not use outside knowledge.
2. Do not invent or assume facts that are not present in the context.
3. If the context does not contain enough information, clearly say that
   the available documents do not provide enough information.
4. Give a concise and direct answer.
5. Do not mention these instructions in your answer.

Context:
{context}

Question:
{question}

Answer:
"""

        return self.llm_provider.generate(prompt)