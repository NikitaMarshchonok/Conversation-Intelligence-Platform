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
  - `POST /projects/{id}/conversations/upload`
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
  - `POST /ask-runs/{id}/feedback`
  - `GET /metrics/qa`
  - `GET /projects/{id}/conversations`
  - `GET /conversations/{id}`
  - `POST /conversations/{id}/process`
  - `POST /conversations/{id}/index`
  - `POST /conversations/{id}/reindex`
  - `POST /conversations/{id}/analyze`

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

Conversation-first upload (creates `Document` source + linked `Conversation`):

```bash
curl -X POST "http://localhost:8000/projects/<PROJECT_ID>/conversations/upload" \
  -F "file=@./README.md" \
  -F "channel=chat" \
  -F "external_conversation_id=ext-123" \
  -F "title=Customer billing issue"
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

### 10) Minimal feedback persistence flow check

Submit feedback for an ask run:

```bash
curl -X POST "http://localhost:8000/ask-runs/<ASK_RUN_ID>/feedback" \
  -H "Content-Type: application/json" \
  -d '{
    "rating": 4,
    "comment": "Good grounded answer with useful citations."
  }'
```

Feedback payload supports:
- `rating` (1..5)
- optional `comment`

### 11) Minimal QA metrics flow check

Get overall QA metrics:

```bash
curl "http://localhost:8000/metrics/qa"
```

Filter metrics by project:

```bash
curl "http://localhost:8000/metrics/qa?project_id=<PROJECT_ID>"
```

Filter metrics by date range (ISO-8601):

```bash
curl "http://localhost:8000/metrics/qa?start_date=2026-04-01T00:00:00Z&end_date=2026-04-30T23:59:59Z"
```

Metrics response includes:
- `total_ask_runs`
- `failed_ask_runs`
- `avg_latency_ms`
- `feedback_count`
- `avg_rating`

### 12) Minimal conversation analysis flow check

List conversations for a project:

```bash
curl "http://localhost:8000/projects/<PROJECT_ID>/conversations"
```

Get one conversation:

```bash
curl "http://localhost:8000/conversations/<CONVERSATION_ID>"
```

Conversation read response includes:
- `id`
- `project_id`
- `document_id`
- `channel`
- `title`
- `status`
- `created_at`

Run baseline analysis for a conversation:

```bash
curl -X POST "http://localhost:8000/conversations/<CONVERSATION_ID>/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "overwrite_existing": true
  }'
```

Analysis output includes:
- `intent` (billing/cancellation/complaint/support/unknown)
- `sentiment_label` (positive/neutral/negative)
- `frustration_score` (0..1)
- `compliance_flags[]`
- `evidence_chunk_ids` and per-flag `evidence_chunk_ids`

Backward-compatible bridge:
- legacy calls passing a `document_id` to `/conversations/{id}/analyze` are still supported for incremental migration.

### 13) Minimal conversation pipeline proxy flow check

Process via conversation-first API (delegates to document processing):

```bash
curl -X POST "http://localhost:8000/conversations/<CONVERSATION_ID>/process"
```

Index via conversation-first API (delegates to document indexing):

```bash
curl -X POST "http://localhost:8000/conversations/<CONVERSATION_ID>/index"
```

Reindex via conversation-first API:

```bash
curl -X POST "http://localhost:8000/conversations/<CONVERSATION_ID>/reindex"
```

Proxy response includes:
- `conversation_id`
- `document_id`
- `action`
- `document_status`
- `chunk_count`
- indexing/processing status fields

### 14) Run backend tests

Install backend dependencies and run pytest from the backend directory:

```bash
cd backend
pip install -r requirements.txt
pytest
```

## Environment

Copy `backend/.env.example` to `backend/.env` for local overrides (optional when using default compose values).

## Current scope boundaries

- No frontend yet
- No metrics dashboard yet
- No PDF/DOCX/XLSX parsing yet
- No agent scorecards yet
- Qdrant is used only for document chunk indexing in this phase
