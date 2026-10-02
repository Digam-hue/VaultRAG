### __init__.py

##### → tells Python that these directories can be treated as packages.
### python3 -m venv .venv
- m: A flag telling Python to run a built-in module as a script.
- venv: The built-in Python module responsible for creating virtual environments.
- .venv: The name given to the hidden folder where the isolated environment files are stored.

### pip freeze > requirements.txt
- This records the packages currently installed in the environment. will store in requirements.txt
- Later, someone can recreate the environment using:    pip install -r requirements.txt

### Running main.py:
- uvicorn app.main:app --reload
- http://127.0.0.1:8000/health
- http://127.0.0.1:8000/docs

### next
- Ctrl+C
- pip install pytest httpx
- • pytest: A popular third-party testing framework used to write and run Python code tests easily.
- • httpx: A modern, fast HTTP client library used to send web requests (like GET and POST) in Python.

- • assert: A Python keyword that checks if a condition is true; if the condition is false, it immediately stops execution and triggers a test failure.

-  Why Path?
from pathlib import Path

- Python's pathlib gives us a clean way to work with file paths.

- Instead of doing complicated string manipulation:

- "data/documents/" + filename

### with path.open("r", encoding="utf-8") as file:

"r" means: read mode.

encoding="utf-8" is important because company documents may eventually contain:
Indian languages
symbols
accented characters
special characters