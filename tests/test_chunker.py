import pytest
from app.ingestion.chunker import chunk_text

def test_chunk_text():
    text = "ABCDEFGHIJ"

    chunks = chunk_text(
        text=text,
        chunk_size=4,
        overlap=1,
    )

    assert chunks == [
        "ABCD",
        "DEFG",
        "GHIJ","J"
    ]
    
def test_small_text():
    text = "ABC"

    chunks = chunk_text(
        text=text,
        chunk_size=10,
        overlap=2,
    )

    assert chunks == ["ABC"]

def test_invalid_chunk_size():
    with pytest.raises(ValueError):
        chunk_text(
            text="ABCDEFGHIJ",
            chunk_size=0,
            overlap=0,
        )


def test_invalid_overlap():
    with pytest.raises(ValueError):
        chunk_text(
            text="ABCDEFGHIJ",
            chunk_size=5,
            overlap=5,
        )