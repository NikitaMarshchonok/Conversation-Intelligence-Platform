from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class DocumentRead(BaseModel):
    id: UUID
    project_id: UUID
    filename: str
    original_name: str
    mime_type: str | None
    size_bytes: int
    storage_path: str
    status: str
    processed_at: datetime | None
    processing_error: str | None
    chunk_count: int
    indexed_at: datetime | None
    indexing_error: str | None
    is_indexed: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DocumentChunkRead(BaseModel):
    id: UUID
    document_id: UUID
    chunk_index: int
    content: str
    char_start: int
    char_end: int
    token_estimate: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DocumentIndexStatusRead(BaseModel):
    id: UUID
    status: str
    chunk_count: int
    is_indexed: bool
    indexed_at: datetime | None
    indexing_error: str | None

    model_config = ConfigDict(from_attributes=True)
