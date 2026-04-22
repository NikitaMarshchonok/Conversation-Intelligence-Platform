from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ConversationRead(BaseModel):
    id: UUID
    project_id: UUID
    document_id: UUID | None
    external_conversation_id: str | None
    channel: str
    title: str | None
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
