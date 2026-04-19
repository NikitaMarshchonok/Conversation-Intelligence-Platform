# ARCHITECTURE.md

## High-level architecture

### Backend layers
1. API layer
2. Service layer
3. Persistence layer
4. Retrieval/indexing layer
5. LLM/AI layer
6. Evaluation layer

### Frontend layers
1. Product pages
2. Feature components
3. API client
4. Typed contracts
5. Internal debug/evaluation views

## Backend modules
- app/api/routes
- app/core
- app/db
- app/models
- app/schemas
- app/services
- app/services/embeddings
- app/services/vector_store
- app/services/reranking
- app/services/llm

## Design rules
- Route handlers must stay thin
- Business logic belongs in services
- No duplicate retrieval logic
- Reuse the same pipeline where possible
- Keep models explicit and typed
- Make provider layers swappable
- Keep migration history consistent

## Future-proofing
Architecture must support:
- multiple data channels
- grounded Q&A
- compliance detection
- coaching analysis
- evaluation and observability
