File

	

What belongs there
ARCHITECTURE.md
Modules, how they connect, and the overall design

PROJECT_PROGRESS.md
Day-by-day progress, completed tasks, and next steps

CHANGELOG.md
Brief record of meaningful code changes

DECISIONS.md
Important design decisions and why we made them

LEARNING.md
Your learning notes: concepts, examples, trade-offs, and things you understand

PROJECT_CONTEXT.md
Project goals, tech stack, current implementation, commands, known issues, and a prompt to resume in a new chat


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

#### assert: 
- A Python keyword that checks if a condition is true; if the condition is false, it immediately stops execution and triggers a test failure.

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


#### raise ValueError(...): Stops execution and crashes the program with a descriptive error message if invalid size inputs are provided.

#### productions minded improvement
if  :
chunks=["", "   "]

Those aren't useful chunks.

We don't want empty chunks entering our future embedding pipeline.
- Validate data at component boundaries rather than letting bad data travel through the entire pipeline
-       for chunk_id, chunk in enumerate(chunks):     
            if not chunk.strip():
                continue


In Pydantic v2, the @model_validator decorator allows you to validate multiple fields together or change the data structure before or after validation. There are two modes: mode='before' (runs before Pydantic parses the data) and mode='after' (runs after field-level validation is complete).
Here are clear examples of how to use both modes.
1. mode='after' (Post-Validation)
Use this when you want to validate relationships between multiple fields after they have already been parsed into their correct types. The function receives self.
python
        from pydantic import BaseModel, model_validator
        from typing_extensions import Self

        class TourRegistration(BaseModel):
            min_age: int
            max_age: int

            @model_validator(mode='after')
            def check_age_range(self) -> Self:
                # Fields are already validated as integers here
                if self.min_age > self.max_age:
                    raise ValueError("min_age cannot be greater than max_age")
                return self
2. mode='before' (Pre-Validation)
Use this when you want to modify incoming data (like a dictionary or JSON) before Pydantic checks the types. The function is a @classmethod and receives the raw input values.
python
from pydantic import BaseModel, model_validator
from typing import Any

        class UserProfile(BaseModel):
            username: str
            bio: str

            @model_validator(mode='before')
            @classmethod
            def set_default_bio(cls, data: Any) -> Any:
                # data is usually a dict representing the incoming payload
                if isinstance(data, dict) and "bio" not in data:
                    data["bio"] = f"Hello, I am {data.get('username', 'a user')}!"
                return data


````markdown
## Pydantic `model_config`

`model_config` = configuration/rules that control how a Pydantic model behaves.

```python
model_config = ConfigDict(
    validate_assignment=True,
    extra="forbid",
)
````

### `validate_assignment=True`

**What:** Validates a field even when it is changed after object creation.

```python
doc = Document(page_content="Hello")
doc.page_content = 123  # ❌ ValidationError
```

Without it, assignment may bypass Pydantic's normal validation.

**Remember:**

> **"If I change it later, validate it."**

---

### `extra="forbid"`

**What:** Rejects fields that are not declared in the model.

```python
Document(
    page_content="Hello",
    author="Digu"   # ❌ not declared
)
```

Other options:

| Option     | Meaning               |
| ---------- | --------------------- |
| `"ignore"` | Ignore unknown fields |
| `"allow"`  | Keep unknown fields   |
| `"forbid"` | Reject unknown fields |

**Remember:**

> **"If I don't know this field, reject it."**

---

### Together

```python
model_config = ConfigDict(
    validate_assignment=True,
    extra="forbid",
)
```

Means:

> **Validate changes + reject unknown fields.**

```text
validate_assignment → protects modifications
extra="forbid"       → protects the schema
```

````markdown
## `sha256_text()`

```python
def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()
````

### What?

Converts a string into a **SHA-256 hash** — a fixed-length hexadecimal string.

```text
"Hello"
   ↓
UTF-8 bytes
   ↓
SHA-256
   ↓
64-character hexadecimal hash
```

### How?

#### 1. `text.encode("utf-8")`

Converts the Python string into **bytes**.

```python
"Hello".encode("utf-8")
# b'Hello'
```

Hash algorithms work on bytes.

#### 2. `hashlib.sha256(...)`

Creates a SHA-256 hash from those bytes.

```python
hashlib.sha256(b"Hello")
```

Returns a hash object.

#### 3. `.hexdigest()`

Converts the hash into a readable hexadecimal string.

```python
hashlib.sha256(b"Hello").hexdigest()
```

Output → **64 hex characters**

### Why use it?

Same input → same hash.

```python
sha256_text("Hello") == sha256_text("Hello")
# True
```

Tiny input change → completely different hash.

```text
"Hello" → hash A
"hello" → hash B
```

### Common use in RAG

Useful for creating a **stable ID/fingerprint** for document text:

```text
document text
     ↓
SHA-256
     ↓
unique-looking content ID
```

For example, useful for **deduplication, caching, or detecting whether content changed**.

### Remember

> **`encode()` → string → bytes**
> **`sha256()` → bytes → hash**
> **`hexdigest()` → hash → readable hex string**


````markdown
## `resolve()` + `is_relative_to()`

```python
path = file_path.resolve()

if not path.is_relative_to(self.documents_dir):
    raise ValueError(
        "File must be inside the documents directory"
    )
````

### What?

Ensures the file being ingested is **inside the allowed documents/knowledge directory**.

### How?

#### `resolve()`

```python
path = file_path.resolve()
```

Converts the path into its **absolute, normalized path**.

Example:

```text
./documents/a.pdf
        ↓
/app/documents/a.pdf
```

This also helps handle things like `..` in paths.

#### `is_relative_to()`

```python
path.is_relative_to(self.documents_dir)
```

Checks:

> "Is this file located inside `documents_dir`?"

Example:

```text
documents_dir = /app/documents

/app/documents/a.pdf
        → True ✓

/home/user/secret.txt
        → False ❌
```

If `False`:

```python
raise ValueError(...)
```

stops the ingestion.

### Why?

**Security / path validation.**

It prevents the ingestion system from reading files outside the intended knowledge directory.

### Remember

> **`resolve()` → get the real absolute path.**
> **`is_relative_to()` → check whether it's inside the allowed directory.**

````markdown
## `relative_to()` + `as_posix()`

```python
source_key = path.relative_to(self.documents_dir).as_posix()
````

### What?

Creates a **stable path/key relative to the documents directory**.

Example:

```text
documents_dir = /app/documents
path          = /app/documents/reports/2026/a.pdf
```

Then:

```text
path.relative_to(documents_dir)
        ↓
reports/2026/a.pdf
```

### `as_posix()` : posix = Portable Operating System Interface X(UniX)

Converts the path into a standard `/`-separated string:

```text
reports/2026/a.pdf
```

Useful for storing paths consistently across operating systems.

### Remember

> **`relative_to()` → remove the common base directory.**
> **`as_posix()` → convert the resulting Path to `/`-style string.**

So `source_key` becomes:

```text
documents root → reports/2026/a.pdf
```

rather than storing the full absolute path.


### Other important terms

* **`Protocol`** → defines a common contract/interface that different embedding providers can follow.
* **Structural typing** → if a class has the required methods with compatible types, it satisfies the `Protocol`; explicit inheritance isn't required.
* **`Sequence[str]`** → ordered collection of strings; accepts both `list[str]` and `tuple[str, ...]`.
* **`...` (Ellipsis)** → placeholder showing the `Protocol` method has no implementation here.
* **Provider interchangeability** → OpenAI, Ollama, HuggingFace, or a custom provider can implement the same interface.
* **Dependency inversion** → RAG code depends on `EmbeddingProvider` (interface), not a specific embedding model.
* **`embed_documents` vs `embed_query`** → separate methods because document and query embeddings may use different processing/instructions.



This is a **pytest test** that checks whether code raises the expected error.

```python
with pytest.raises(ValueError, match="Query text cannot be empty"):
    service.embed_query("   ")
```

### Meaning

> “When I call `embed_query("   ")`, I **expect a `ValueError`** with the message `"Query text cannot be empty"`.”

Breakdown:

* `pytest.raises(ValueError)` → expect a `ValueError`
* `match="Query text cannot be empty"` → error message should match this text
* `service.embed_query("   ")` → the actual code being tested
* `"   "` → only spaces, so the function should consider it **empty**

### Example

If your function does:

```python
def embed_query(text):
    if not text.strip():
        raise ValueError("Query text cannot be empty")
```

Then this test passes:

```python
with pytest.raises(ValueError, match="Query text cannot be empty"):
    service.embed_query("   ")
```

If `embed_query()` **doesn't raise an error**, the test fails.

If it raises:

```python
ValueError("Something went wrong")
```
### Day  7
```
if hasattr(result, "tolist"):
            result = result.tolist()
```
checking for a NumPy array (or a similar library like pandas).
The hasattr(result, "tolist") function checks if the result object has a method named .tolist().
- next can be usefullfor serializabl like passing through json so first convert to list and then required format 


```
DEBUG    → detailed debugging information
INFO     → normal information
WARNING  → something potentially problematic
ERROR    → an error occurred
CRITICAL → serious error
```

# New Learnings — FastAPI & Python

## 1. `os.getenv()`

Reads an environment variable and optionally provides a default value.

```python
model = os.getenv(
    "HF_EMBEDDING_MODEL",
    "BAAI/bge-small-en-v1.5"
)
```

* If `HF_EMBEDDING_MODEL` exists → use its value.
* Otherwise → use `"BAAI/bge-small-en-v1.5"`.

---

## 2. `@staticmethod` vs `@classmethod`

```python
class Example:

    @staticmethod
    def add(a, b):
        return a + b

    @classmethod
    def name(cls):
        return cls.__name__
```

* `staticmethod` → receives **nothing automatically**.
* `classmethod` → receives the **class as `cls`**.
* Normal method → receives the **object as `self`**.

```text
self → object
cls  → class
static → nothing
```

---

## 3. Pydantic `field_validator`

```python
class Request(BaseModel):
    text: str

    @field_validator("text")
    @classmethod
    def validate_text(cls, value):
        if not value.strip():
            raise ValueError("Text cannot be blank")
        return value
```

`"text"` tells Pydantic **which field** to validate.

`validate_text` is simply the **function name**. It can have any valid name.

```text
"field name" → text
"validator function" → validate_text()
```

---

## 4. Validator `mode`

```python
@field_validator("text", mode="before")
```

Runs before Pydantic's normal validation:

```text
Raw input → Your validator → Pydantic validation
```

```python
@field_validator("text", mode="after")
```

Runs after Pydantic's normal validation.

```text
Raw input → Pydantic validation → Your validator
```

`mode="after"` is the default.

---

## 5. `Field()`

```python
text: str = Field(
    min_length=1,
    max_length=10_000
)
```

Adds validation constraints/metadata to a Pydantic field.

---

## 6. `@lru_cache`

```python
@lru_cache(maxsize=1)
def get_service():
    return EmbeddingService()
```

Caches the function result so an expensive object doesn't need to be recreated every time.

```text
First call  → create object → cache
Next calls  → return cached object
```

---

## 7. FastAPI `APIRouter`

```python
router = APIRouter(
    prefix="/embeddings",
    tags=["Embeddings"]
)

@router.post("/query")
def query():
    ...
```

Final endpoint:

```text
POST /embeddings/query
```

* `prefix` → common path for routes.
* `tags` → organizes Swagger/OpenAPI docs.
* `@router.post()` → connects a POST request to a Python function.

---

## 8. FastAPI Response Model

```python
class Response(BaseModel):
    model: str
    dimensions: int
    embedding: list[float]

@router.post(
    "/query",
    response_model=Response
)
def query():
    ...
```

`response_model` defines and validates the structure of the API response.

---

## 9. HTTP Status Codes

Example server log:

```text
POST /embeddings/query HTTP/1.1" 200 OK
```

Important codes:

```text
200 → Success
201 → Created
400 → Bad Request
401 → Unauthorized
403 → Forbidden
404 → Not Found
422 → Validation Error
500 → Server Error
502 → Upstream/Provider Error
503 → Service Unavailable
```

Example:

```text
GET /ws/ws → 404 Not Found
```

means the requested route `/ws/ws` doesn't exist.

---

## 10. Uvicorn Access Log

```text
INFO: 127.0.0.1:58706 - "POST /embeddings/query HTTP/1.1" 200 OK
```

Meaning:

```text
INFO              → log level
127.0.0.1         → localhost / this computer
58706             → client's temporary port
POST              → HTTP method
/embeddings/query → requested endpoint
HTTP/1.1          → HTTP protocol version
200 OK            → request succeeded
```
## FastAPI Dependency Injection & Testing

### 1. `Depends()`

`Depends()` tells FastAPI to provide a dependency automatically.

```python
def endpoint(
    service: EmbeddingService = Depends(get_embedding_service)
):
    ...
```

Flow:

```text
Request → FastAPI → get_embedding_service() → service → endpoint
```

### 2. `dependency_overrides`

Used in tests to replace a real dependency with a fake/test dependency.

```python
app.dependency_overrides[get_embedding_service] = fake_service
```

Useful for avoiding real APIs, models, databases, API keys, etc.

### 3. `lambda`

A short anonymous function.

```python
lambda: EmbeddingService(FakeEmbeddingProvider())
```

Equivalent to:

```python
def fake_service():
    return EmbeddingService(FakeEmbeddingProvider())
```

### 4. Complete Test Pattern

```python
app.dependency_overrides[get_embedding_service] = (
    lambda: EmbeddingService(FakeEmbeddingProvider())
)

response = client.post(
    "/embeddings/query",
    json={"text": "How does semantic search work?"},
)
```

**Key idea:**
`Depends()` → inject dependency in production.
`dependency_overrides` → replace it during testing.
