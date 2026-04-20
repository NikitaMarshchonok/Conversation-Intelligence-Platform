from uuid import UUID

from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    query: str = Field(min_length=1)
    project_id: UUID
    top_k: int = Field(default=5, ge=1, le=50)
    document_ids: list[UUID] | None = None


class AskCitation(BaseModel):
    document_id: UUID
    chunk_id: UUID
    chunk_index: int
    snippet: str


class AskSupportingResult(BaseModel):
    document_id: UUID
    chunk_id: UUID
    chunk_index: int
    score: float
    content: str


class AskResponse(BaseModel):
    answer: str
    citations: list[AskCitation]
    supporting_results: list[AskSupportingResult]
