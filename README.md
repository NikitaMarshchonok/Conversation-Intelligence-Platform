# Conversation Intelligence Platform

Phase 1 foundation baseline for a production-style Conversation Intelligence Platform.

## What is included now

- FastAPI backend skeleton with modular layers (`api`, `services`, `models`, `schemas`, `db`, `core`)
- PostgreSQL + Qdrant + backend in `docker-compose`
- SQLAlchemy session wiring via environment-based config
- Alembic setup with initial migration
- Minimal core entities: `Project`, `Document`
- Minimal endpoints:
  - `GET /health`
  - `GET /projects`
  - `POST /projects`
  - `GET /projects/{id}`
  - `POST /projects/{id}/documents/upload`
  - `GET /projects/{id}/documents`
  - `GET /documents/{id}`
  - `POST /documents/{id}/process`
  - `GET /documents/{id}/chunks`
  - `POST /documents/{id}/index`
  - `POST /documents/{id}/reindex`
  - `GET /documents/{id}/index-status`
  - `POST /search`
  - `POST /ask`
  - `GET /ask-runs`
  - `GET /ask-runs/{id}`

## Local run

### 1) Start infrastructure + backend

```bash
docker compose up --build
```

Backend: [http://localhost:8000](http://localhost:8000)  
Swagger: [http://localhost:8000/docs](http://localhost:8000/docs)

### 2) Apply migrations

Open a second terminal in the project root:

```bash
docker compose exec backend alembic upgrade head
```

### 3) Quick API check

```bash
curl http://localhost:8000/health
```

Expected response:

```json
{"status":"ok"}
```

### 4) Minimal upload flow check

Create a project:

```bash
curl -X POST http://localhost:8000/projects \
  -H "Content-Type: application/json" \
  -d '{"name":"Demo Project","description":"Upload test"}'
```

Copy the returned project `id`, then upload a file:

```bash
curl -X POST "http://localhost:8000/projects/<PROJECT_ID>/documents/upload" \
  -F "file=@./README.md"
```

List project documents:

```bash
curl "http://localhost:8000/projects/<PROJECT_ID>/documents"
```

Get a single document:

```bash
curl "http://localhost:8000/documents/<DOCUMENT_ID>"
```

### 5) Minimal processing flow check

Process the uploaded document:

```bash
curl -X POST "http://localhost:8000/documents/<DOCUMENT_ID>/process"
```

List document chunks:

```bash
curl "http://localhost:8000/documents/<DOCUMENT_ID>/chunks"
```

Current processing supports only simple text-based files (`.txt`, `.md`, `.csv`, `.json`, `.log`, `.yaml`, `.yml`, `.html`).

### 6) Minimal indexing flow check

Index a processed document:

```bash
curl -X POST "http://localhost:8000/documents/<DOCUMENT_ID>/index"
```

Check index status:

```bash
curl "http://localhost:8000/documents/<DOCUMENT_ID>/index-status"
```

Reindex the document (removes old vectors before upsert):

```bash
curl -X POST "http://localhost:8000/documents/<DOCUMENT_ID>/reindex"
```

### 7) Minimal retrieval flow check

Search indexed chunks by project:

```bash
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "foundation baseline",
    "project_id": "<PROJECT_ID>",
    "top_k": 5
  }'
```

Search with optional document filter:

```bash
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "indexing",
    "project_id": "<PROJECT_ID>",
    "top_k": 5,
    "document_ids": ["<DOCUMENT_ID>"]
  }'
```

### 8) Minimal grounded ask flow check

Ask a grounded question over retrieved chunks:

```bash
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What does this project currently support?",
    "project_id": "<PROJECT_ID>",
    "top_k": 5
  }'
```

Ask with optional document filter:

```bash
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What indexing behavior is implemented?",
    "project_id": "<PROJECT_ID>",
    "top_k": 5,
    "document_ids": ["<DOCUMENT_ID>"]
  }'
```

The ask response includes:
- `answer`
- `citations[]`
- `supporting_results[]`
- `retrieved_order[]`
- `reranked_order[]`

Reranking baseline:
- uses retrieved top-k candidates only
- applies a local keyword-based reranker
- preserves the same chunk references (only order changes)

### 9) Minimal evaluation persistence flow check

Every `/ask` call now persists an ask run and citations.

List ask runs:

```bash
curl "http://localhost:8000/ask-runs?offset=0&limit=20"
```

Filter ask runs by project:

```bash
curl "http://localhost:8000/ask-runs?offset=0&limit=20&project_id=<PROJECT_ID>"
```

Get ask run details:

```bash
curl "http://localhost:8000/ask-runs/<ASK_RUN_ID>"
```

Stored ask-run fields include:
- `query`
- `answer`
- `status`
- `latency_ms`
- `retrieved_chunk_ids`
- `reranked_chunk_ids`
- `cited_chunk_ids`
- `citations[]`

## Environment

Copy `backend/.env.example` to `backend/.env` for local overrides (optional when using default compose values).

## Current scope boundaries

- No frontend yet
- No feedback/metrics yet
- No PDF/DOCX/XLSX parsing yet
- Qdrant is used only for document chunk indexing in this phase
