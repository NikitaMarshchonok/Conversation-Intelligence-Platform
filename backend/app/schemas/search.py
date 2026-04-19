from uuid import UUID

from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    query: str = Field(min_length=1)
    project_id: UUID
    top_k: int = Field(default=10, ge=1, le=100)
    document_ids: list[UUID] | None = None


class SearchResultItem(BaseModel):
    document_id: UUID
    chunk_id: UUID
    chunk_index: int
    score: float
    content: str


class SearchResponse(BaseModel):
    query: str
    top_k: int
    total_results: int
    results: list[SearchResultItem]
