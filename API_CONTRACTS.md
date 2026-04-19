# API_CONTRACTS.md

## Required endpoints

### Health
- GET /health

### Projects
- GET /projects
- POST /projects
- GET /projects/{id}

### Upload / documents
- POST /projects/{id}/documents/upload
- GET /projects/{id}/documents

### Processing visibility
- GET /documents/{id}
- GET /documents/{id}/chunks

### Indexing
- POST /documents/{id}/index
- POST /documents/{id}/reindex
- GET /documents/{id}/index-status

### Search
- POST /search

### Ask
- POST /ask

### Evaluation
- GET /ask-runs
- GET /ask-runs/{id}
- POST /ask-runs/{id}/feedback
- GET /metrics/qa

## Future domain endpoints
### Conversations
- GET /projects/{id}/conversations
- GET /conversations/{id}
- POST /projects/{id}/conversations/upload

### QA / compliance
- GET /conversations/{id}/compliance
- POST /conversations/{id}/analyze

### Coaching
- GET /agents/{id}/scorecard
- GET /agents/{id}/coaching
