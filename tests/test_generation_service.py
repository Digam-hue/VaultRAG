from app.services.generation_service import GenerationService


class FakeLLMProvider:
    def __init__(self):
        self.prompts = []

    def generate(self, prompt: str) -> str:
        self.prompts.append(prompt)
        return "Employees receive 30 days of annual leave."


def test_generation_uses_retrieved_context():
    provider = FakeLLMProvider()
    service = GenerationService(provider)

    documents = [
        {
            "page_content": "Employees receive 30 days of annual leave.",
            "metadata": {
                "source": "leave_policy.txt",
            },
            "distance": 0.1,
        }
    ]

    answer = service.generate_answer(
        question="How many annual leave days are provided?",
        documents=documents,
    )

    assert answer == "Employees receive 30 days of annual leave."
    assert len(provider.prompts) == 1
    assert "30 days of annual leave" in provider.prompts[0]
    assert "How many annual leave days are provided?" in provider.prompts[0]


def test_generation_handles_no_documents():
    provider = FakeLLMProvider()
    service = GenerationService(provider)

    answer = service.generate_answer(
        question="What is the leave policy?",
        documents=[],
    )

    assert "don't have enough information" in answer
    assert provider.prompts == []


def test_generation_rejects_blank_question():
    provider = FakeLLMProvider()
    service = GenerationService(provider)

    try:
        service.generate_answer(
            question="   ",
            documents=[],
        )
        assert False
    except ValueError as exc:
        assert str(exc) == "Question cannot be empty"