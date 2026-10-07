import os

from dotenv import load_dotenv
from groq import Groq

load_dotenv()


class GroqLLMProvider:
    """Generate text using a Groq-hosted language model."""

    def __init__(
        self,
        model: str | None = None,
    ) -> None:
        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            raise ValueError("GROQ_API_KEY is not configured")

        self.model = model or os.getenv(
            "GROQ_MODEL",
            "openai/gpt-oss-120b",
        )

        self.client = Groq(api_key=api_key)

    def generate(self, prompt: str) -> str:
        if not prompt.strip():
            raise ValueError("Prompt cannot be empty")

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            temperature=0,
        )

        content = response.choices[0].message.content

        if not content:
            raise ValueError("LLM returned an empty response")

        return content.strip()