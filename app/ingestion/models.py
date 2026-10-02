from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class Document(BaseModel):
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
    )

    page_content: str = Field(min_length=1)
    metadata: dict[str, Any] = Field(default_factory=dict)