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

## Environment

Copy `backend/.env.example` to `backend/.env` for local overrides (optional when using default compose values).

## Current scope boundaries

- No frontend yet
- No processing/chunking/indexing/search/ask yet
- Qdrant is provisioned but not used in this phase
