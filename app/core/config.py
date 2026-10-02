from pydantic import BaseModel,Field,model_validator

class IngestionConfig(BaseModel):
    chunk_size: int = Field(default=800, gt=0)
    chunk_overlap: int = Field(default=120, ge=0)
    
    @model_validator(mode='after')
    def validate_overlap(self):
        if self.chunk_overlap >= self.chunk_size:
            raise ValueError(
                "chunk_overlap must be smaller than chunk_size"
            )
        return self
    

class EmbeddingConfig(BaseModel):
    batch_size: int = Field(default=32, gt=0)
    expected_dimensions: int | None = Field(default=None, gt=0)