from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class AskRunCitationRead(BaseModel):
    id: UUID
    ask_run_id: UUID
    document_id: UUID
    chunk_id: UUID
    chunk_index: int
    snippet: str
    citation_order: int

    model_config = ConfigDict(from_attributes=True)


class AskRunListItemRead(BaseModel):
    id: UUID
    project_id: UUID
    query: str
    answer: str
    status: str
    latency_ms: int
    retrieved_chunk_ids: list[UUID]
    reranked_chunk_ids: list[UUID]
    cited_chunk_ids: list[UUID]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AskRunRead(AskRunListItemRead):
    citations: list[AskRunCitationRead]
