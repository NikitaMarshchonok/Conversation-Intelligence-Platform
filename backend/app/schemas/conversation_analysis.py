from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ConversationAnalyzeRequest(BaseModel):
    overwrite_existing: bool = True


class ComplianceFlagResult(BaseModel):
    flag_type: str
    is_triggered: bool
    evidence_chunk_ids: list[UUID]
    explanation: str | None


class ConversationAnalyzeResponse(BaseModel):
    conversation_id: UUID
    intent: str
    sentiment_label: str
    frustration_score: float
    evidence_chunk_ids: list[UUID]
    compliance_flags: list[ComplianceFlagResult]
    analyzed_at: datetime
