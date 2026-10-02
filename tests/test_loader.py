from app.ingestion.loader import load_text_file


def test_load_text_file():
    file_path = "data/documents/leave_poicy.txt"

    content = load_text_file(file_path)

    assert content != ""
    assert "Employee Leave Policy" in content