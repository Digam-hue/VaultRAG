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

HNSW = Hierarchical Navigable Small World

It is an indexing algorithm/data structure used for fast approximate nearest-neighbor (ANN) search.

In your ChromaDB code:

metadata={"hnsw:space": "cosine"}

it means ChromaDB's HNSW vector index will use cosine distance/similarity to compare embedding vectors.


### ChromaDB `upsert()`

```python
self.collection.upsert(
    ids=ids,
    documents=texts,
    metadatas=metadatas,
    embeddings=vectors,
)
```

**Purpose:** Add or update chunks in the ChromaDB collection.

* `ids` → unique ID for each chunk, e.g. `"doc_101:0"`
* `documents` → actual chunk text
* `metadatas` → extra information about the chunk, e.g. source, page, document ID
* `embeddings` → vector representation of each chunk

**`upsert` = `insert + update`**

* ID doesn't exist → **insert** new record
* ID already exists → **update/replace** that record

Example:

```text
ID:         doc_101:0
Document:   "Python is used in ML."
Metadata:   {"source": "notes.pdf", "page": 2}
Embedding:  [0.12, -0.45, 0.78, ...]
```

So remember:

> **`upsert()` stores the chunk + its embedding + metadata in ChromaDB, creating it if new or updating it if the ID already exists.**




# ChromaDB & Pytest — Quick Revision

## ChromaDB

### PersistentClient

```python
chromadb.PersistentClient(path="data/chroma")
```

* Creates/opens a **persistent local ChromaDB**.
* Data is stored on **disk**, so it survives program restarts.
* ChromaDB still uses **RAM while running**.

### Collection

```python
client.get_or_create_collection(name="chunks")
```

* A collection stores **documents/chunks + embeddings + metadata + IDs**.
* Similar to a table conceptually, but it is a vector database collection.

### `get_or_create_collection()`

* If collection exists → **open/reuse it**.
* If it doesn't exist → **create it**.

### HNSW

**HNSW = Hierarchical Navigable Small World**

* A graph-based index for **fast approximate nearest-neighbor vector search**.
* Commonly used to find similar embeddings efficiently.

```python
metadata={"hnsw:space": "cosine"}
```

* Configures the vector distance/space as **cosine**.

### `embedding_function=None`

```python
embedding_function=None
```

* Tells ChromaDB **not to generate embeddings itself**.
* Your application provides the already-generated `embeddings`.

---

## ChromaDB Data Operations

### `upsert()`

```python
collection.upsert(
    ids=ids,
    documents=texts,
    metadatas=metadatas,
    embeddings=vectors
)
```

* **Upsert = Insert + Update**
* New ID → insert.
* Existing ID → update/replace.
* The lists are matched by position:

```text
ids[0] ↔ documents[0] ↔ metadatas[0] ↔ embeddings[0]
```

### Chunk ID

```python
f"{document_id}:{chunk_id}"
```

Example:

```text
doc_101:0
doc_101:1
doc_101:2
```

* `document_id` → identifies the original document.
* `chunk_id` → identifies a particular chunk inside that document.
* Together they provide a useful unique chunk ID.

---

## Vector Similarity Search

### `collection.query()`

```python
collection.query(
    query_embeddings=[[...]],
    n_results=top_k,
    include=["documents", "metadatas", "distances"]
)
```

* Searches ChromaDB for vectors most similar to the query embedding.
* `n_results` → number of results requested.
* `documents` → matched chunk text.
* `metadatas` → information associated with chunks.
* `distances` → how far each result is from the query according to the configured distance metric.

### Why `[[...]]`?

```python
query_embeddings=[[0.1, 0.2, 0.3]]
```

* Outer list = **list of queries**.
* Inner list = **one query's embedding vector**.

### Chroma query result indexing

```python
result["documents"][0][i]
```

* `[0]` → results belonging to the **first query**.
* `[i]` → the **i-th matching chunk**.

---

## Converting Chroma Results

```python
matches.append({
    "page_content": text,
    "metadata": result["metadatas"][0][i],
    "distance": result["distances"][0][i],
})
```

* Converts Chroma's nested result format into a simpler application format.
* `page_content` → actual retrieved text.
* `metadata` → source/document information.
* `distance` → similarity distance.

---

## Metadata

```python
metadata = {
    "document_id": "doc1",
    "chunk_id": 0,
    "source": "handbook.txt"
}
```

* Metadata describes a chunk.
* Chroma metadata supports supported **primitive/simple values** such as strings, integers, floats, and booleans.
* Arbitrary nested Python objects such as dictionaries generally cannot be directly stored as metadata.

---

# Pytest

### Test Discovery

```python
def test_add_and_search_documents():
```

* Pytest automatically discovers functions whose names start with **`test_`**.
* You don't manually call these test functions.

```text
pytest
  ↓
find test_* functions
  ↓
call them
  ↓
check assertions
```

### Pytest Fixture

```python
def test_search(tmp_path):
```

* `tmp_path` is a **pytest fixture**.
* Pytest creates a temporary directory and automatically passes it to the test.

Conceptually:

```python
tmp_path = temporary_directory
test_search(tmp_path)
```

### `tmp_path` in ChromaDB Tests

```python
ChromaVectorStore(
    persist_directory=tmp_path / "vectors"
)
```

* Gives each test an isolated temporary database location.
* Prevents test data from polluting your real/local database.

---

## `pytest.raises()`

```python
with pytest.raises(ValueError, match="top_k"):
    store.similarity_search(..., top_k=0)
```

* Tests that a specific exception **must occur**.
* `ValueError` → expected exception type.
* `match="top_k"` → expected text should appear in the error message.
* If the error doesn't occur → test fails.
* If a different error occurs → test fails.

### `assert`

```python
assert len(results) == 1
```

* Checks an expected condition.
* `True` → test passes that assertion.
* `False` → test fails.

---

## Helper Function vs Test Function

```python
def make_document(...):
```

* Normal helper function.
* **You call it manually.**

```python
def test_add_and_search_documents(...):
```

* Test function.
* **Pytest calls it automatically.**

```text
make_document()       → YOU call
store.add_documents() → YOU call
similarity_search()   → YOU call

test_*()              → PYTEST calls
```


# FastAPI & Testing — Key Learnings

## 1. FastAPI Route Definition

```python
@router.post("/search", response_model=SearchResponse)
```

* `@` → Python decorator; registers the function as an API route.
* `router.post()` → endpoint accepts **HTTP POST** requests.
* `"/search"` → URL path.
* `response_model=SearchResponse` → FastAPI validates/structures the returned response using the Pydantic model.

**Mental model:** `POST + path → endpoint function → response schema`.

---

## 2. GET vs POST

* **GET** → normally used to **retrieve/read** data; parameters commonly go in the URL.

  ```http
  GET /search?query=python
  ```
* **POST** → commonly used when **sending data to the server for processing**; data usually goes in the request body.

  ```json
  {"query": "python", "top_k": 5}
  ```

For complex search/RAG requests, `POST` is commonly more suitable because the request can contain structured data.

---

## 3. FastAPI Dependency Injection

```python
service: RetrievalService = Depends(get_retrieval_service)
```

Meaning:

> "FastAPI, obtain a `RetrievalService` by calling `get_retrieval_service()` and inject it into `service`."

Flow:

```text
Request
  ↓
FastAPI
  ↓
get_retrieval_service()
  ↓
RetrievalService object
  ↓
service.search(...)
```

`Depends()` lets the endpoint receive required objects without manually creating them inside the endpoint.

---

## 4. `TestClient`

```python
client = TestClient(app)
```

Creates a test HTTP client connected directly to the FastAPI application.

```python
response = client.post("/search", json=data)
```

You can test API endpoints **without starting Uvicorn separately**.

```text
pytest → TestClient → FastAPI app
```

---

## 5. Dependency Overrides in Tests

FastAPI dependencies can be replaced during testing:

```python
app.dependency_overrides[
    get_retrieval_service
] = fake_retrieval_service
```

Instead of:

```text
get_retrieval_service()
      ↓
Real service
```

the test gets:

```text
fake_retrieval_service()
      ↓
Fake service
```

Useful when the real dependency would involve databases, ChromaDB, external APIs, embeddings, etc.

---

## 6. `dependency_overrides.clear()`

```python
app.dependency_overrides.clear()
```

Removes all dependency replacements.

Used to prevent one test's fake dependency from affecting another test.

```python
def setup_function():
    app.dependency_overrides.clear()

def teardown_function():
    app.dependency_overrides.clear()
```

* `setup_function()` → pytest runs it **before each test**.
* `teardown_function()` → pytest runs it **after each test**.

This provides **test isolation**.

---

## 7. Filename Path-Safety Check

```python
if (
    Path(request.filename).name != request.filename
    or request.filename in {".", ".."}
):
    raise HTTPException(status_code=400)
```

Purpose: accept a **filename only**, not an arbitrary filesystem path.

```text
file.txt          → ✅
data/file.txt     → ❌
/home/user/a.txt  → ❌
..               → ❌
.                → ❌
```

`Path(...).name` extracts only the final filename.

This prevents directory/path traversal such as:

```text
../../secret.txt
```

---

# 8. Running FastAPI with Uvicorn

```bash
uvicorn app.main:app --reload
```

Breakdown:

```text
app.main
   ↓
Python module: app/main.py

:
   ↓

app
   ↓
FastAPI application object
```

So:

```text
app.main:app
```

means:

> Import `app.main` and get the `app` object from it.

`--reload` watches for code changes and reloads the application during development.

---

# 9. Server vs Application

These are different:

```text
Uvicorn
  ↓
ASGI Server
  ↓
Runs/listens for HTTP requests

FastAPI
  ↓
Web application/framework
  ↓
Handles routing, validation, dependencies, etc.
```

**Uvicorn is the server; FastAPI is the application.**

---

# 10. ASGI

ASGI is the interface between an ASGI server such as Uvicorn and an application such as FastAPI.

```text
Uvicorn
   ↕
 ASGI
   ↕
FastAPI
```

This allows the server and framework to communicate using a standard interface.

---

# 11. `127.0.0.1:8000`

When Uvicorn starts:

```text
http://127.0.0.1:8000
```

* `127.0.0.1` → **this same computer** (loopback address).
* `8000` → **port** where Uvicorn is listening.
* `localhost` normally resolves to `127.0.0.1`.

Think:

```text
127.0.0.1 → Which machine?
8000       → Which service/port?
```

---

# 12. Socket & Listening

Uvicorn asks the operating system for a **network socket** and binds it to:

```text
127.0.0.1:8000
```

Then it listens for incoming connections.

Conceptually:

```text
Uvicorn
   ↓
Socket
   ↓
127.0.0.1:8000
   ↓
WAIT for requests
```

If another process is already using the same port, you'll get:

```text
Address already in use
```

---

# 13. Actual Request Flow

When you open:

```text
http://127.0.0.1:8000/
```

the real flow is approximately:

```text
Browser
   ↓
HTTP request
   ↓
Operating System / Socket
   ↓
Uvicorn
   ↓
ASGI
   ↓
FastAPI
   ↓
Router
   ↓
Matching endpoint
   ↓
Your function
   ↓
Response
   ↓
Uvicorn
   ↓
Browser
```

For:

```python
@app.get("/")
def home():
    return {"message": "Hello"}
```

the browser sends:

```http
GET /
```

FastAPI matches:

```text
GET + /
   ↓
home()
```

and converts the returned Python data into an HTTP response, typically JSON.

---

# 14. `localhost` vs `0.0.0.0`

```bash
uvicorn app.main:app
```

normally listens on:

```text
127.0.0.1:8000
```

Only the local machine can normally access it.

Using:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

means:

> Listen on available network interfaces.

Then another device on the same network may access the machine through its LAN IP, e.g.:

```text
http://192.168.1.20:8000
```

---

# 15. `--reload` Mental Model

Without reload:

```text
Start Uvicorn
    ↓
Import application
    ↓
Listen
    ↓
Keep running
```

With `--reload`:

```text
Start
 ↓
Watch files
 ↓
File changed?
 ↓ yes
Reload application
```

It is mainly a **development convenience**, not something normally used as the production server setup.

---

## One Big Mental Model

```text
uvicorn app.main:app
        ↓
Import app.main
        ↓
Get FastAPI `app`
        ↓
Uvicorn starts ASGI server
        ↓
OS creates/listens on socket
        ↓
127.0.0.1:8000
        ↓
Client sends HTTP request
        ↓
Uvicorn receives it
        ↓
ASGI → FastAPI
        ↓
Router finds endpoint
        ↓
Dependencies are injected
        ↓
Endpoint executes
        ↓
Response is created
        ↓
Uvicorn sends HTTP response
        ↓
Client receives it
```

**Core idea:**
`Client → Uvicorn (server) → ASGI → FastAPI (application) → Router → Endpoint → Response → Client`
