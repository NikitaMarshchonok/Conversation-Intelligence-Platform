from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models.compliance_flag import ComplianceFlag
from app.models.conversation_insight import ConversationInsight
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.schemas.conversation_analysis import (
    ComplianceFlagResult,
    ConversationAnalyzeRequest,
    ConversationAnalyzeResponse,
)


INTENT_KEYWORDS: dict[str, list[str]] = {
    "billing": ["bill", "billing", "invoice", "charge", "payment", "refund"],
    "cancellation": ["cancel", "termination", "terminate", "unsubscribe", "close account"],
    "complaint": ["complaint", "unhappy", "bad service", "disappointed", "frustrated"],
    "support": ["help", "issue", "problem", "error", "support", "cannot", "can't"],
}

POSITIVE_TERMS = ["thanks", "great", "good", "helpful", "resolved", "appreciate"]
NEGATIVE_TERMS = ["angry", "bad", "terrible", "frustrated", "upset", "disappointed", "not working", "cancel"]


class ConversationAnalysisService:
    @staticmethod
    def analyze_conversation(
        db: Session,
        conversation_id: UUID,
        payload: ConversationAnalyzeRequest,
    ) -> ConversationAnalyzeResponse:
        conversation = db.get(Document, conversation_id)
        if conversation is None:
            raise ValueError("Conversation not found")

        chunks_stmt = (
            select(DocumentChunk)
            .where(DocumentChunk.document_id == conversation_id)
            .order_by(DocumentChunk.chunk_index.asc())
        )
        chunks = list(db.scalars(chunks_stmt).all())
        if not chunks:
            raise ValueError("Conversation has no chunks. Process the document first.")

        if payload.overwrite_existing:
            db.execute(delete(ComplianceFlag).where(ComplianceFlag.conversation_id == conversation_id))
            db.execute(delete(ConversationInsight).where(ConversationInsight.conversation_id == conversation_id))

        combined_text = "\n".join(chunk.content for chunk in chunks).lower()
        intent, intent_evidence = ConversationAnalysisService._detect_intent(chunks)
        sentiment_label = ConversationAnalysisService._detect_sentiment(combined_text)
        frustration_score = ConversationAnalysisService._compute_frustration_score(combined_text)

        insight = ConversationInsight(
            conversation_id=conversation_id,
            intent=intent,
            sentiment_label=sentiment_label,
            frustration_score=frustration_score,
            evidence_chunk_ids=intent_evidence,
        )
        db.add(insight)

        compliance_results = ConversationAnalysisService._build_compliance_flags(chunks=chunks, combined_text=combined_text)
        for item in compliance_results:
            db.add(
                ComplianceFlag(
                    conversation_id=conversation_id,
                    flag_type=item.flag_type,
                    is_triggered=item.is_triggered,
                    evidence_chunk_ids=item.evidence_chunk_ids,
                    explanation=item.explanation,
                )
            )

        db.commit()
        db.refresh(insight)

        return ConversationAnalyzeResponse(
            conversation_id=conversation_id,
            intent=insight.intent,
            sentiment_label=insight.sentiment_label,
            frustration_score=insight.frustration_score,
            evidence_chunk_ids=insight.evidence_chunk_ids,
            compliance_flags=compliance_results,
            analyzed_at=datetime.now(timezone.utc),
        )

    @staticmethod
    def _detect_intent(chunks: list[DocumentChunk]) -> tuple[str, list[UUID]]:
        best_intent = "unknown"
        best_score = 0
        best_evidence: list[UUID] = []

        for intent, keywords in INTENT_KEYWORDS.items():
            evidence_ids: list[UUID] = []
            score = 0
            for chunk in chunks:
                content_lower = chunk.content.lower()
                if any(keyword in content_lower for keyword in keywords):
                    evidence_ids.append(chunk.id)
                    score += sum(content_lower.count(keyword) for keyword in keywords)
            if score > best_score:
                best_score = score
                best_intent = intent
                best_evidence = evidence_ids

        return best_intent, best_evidence

    @staticmethod
    def _detect_sentiment(text: str) -> str:
        positive_hits = sum(text.count(term) for term in POSITIVE_TERMS)
        negative_hits = sum(text.count(term) for term in NEGATIVE_TERMS)
        if negative_hits > positive_hits and negative_hits > 0:
            return "negative"
        if positive_hits > negative_hits and positive_hits > 0:
            return "positive"
        return "neutral"

    @staticmethod
    def _compute_frustration_score(text: str) -> float:
        negative_hits = sum(text.count(term) for term in NEGATIVE_TERMS)
        escalation_hits = sum(text.count(term) for term in ["manager", "supervisor", "escalate", "escalation"])
        exclamation_hits = text.count("!")
        raw_score = (negative_hits * 0.2) + (escalation_hits * 0.25) + (exclamation_hits * 0.03)
        return max(0.0, min(1.0, round(raw_score, 3)))

    @staticmethod
    def _build_compliance_flags(chunks: list[DocumentChunk], combined_text: str) -> list[ComplianceFlagResult]:
        first_segment = combined_text[:300]
        has_greeting = any(term in first_segment for term in ["hello", "hi", "good morning", "good afternoon", "welcome"])
        refund_evidence = ConversationAnalysisService._find_evidence(chunks, ["refund", "reimburse", "chargeback"])
        escalation_evidence = ConversationAnalysisService._find_evidence(chunks, ["manager", "supervisor", "escalate", "escalation"])
        cancellation_evidence = ConversationAnalysisService._find_evidence(
            chunks,
            ["cancel", "termination", "terminate", "switch", "leave"],
        )

        return [
            ComplianceFlagResult(
                flag_type="missing_greeting",
                is_triggered=not has_greeting,
                evidence_chunk_ids=[],
                explanation="No greeting phrase detected near conversation start." if not has_greeting else None,
            ),
            ComplianceFlagResult(
                flag_type="refund_mentioned",
                is_triggered=bool(refund_evidence),
                evidence_chunk_ids=refund_evidence,
                explanation="Refund-related language found." if refund_evidence else None,
            ),
            ComplianceFlagResult(
                flag_type="escalation_requested",
                is_triggered=bool(escalation_evidence),
                evidence_chunk_ids=escalation_evidence,
                explanation="Escalation request indicators found." if escalation_evidence else None,
            ),
            ComplianceFlagResult(
                flag_type="cancellation_risk",
                is_triggered=bool(cancellation_evidence),
                evidence_chunk_ids=cancellation_evidence,
                explanation="Cancellation or churn-risk language found." if cancellation_evidence else None,
            ),
        ]

    @staticmethod
    def _find_evidence(chunks: list[DocumentChunk], keywords: list[str]) -> list[UUID]:
        evidence_ids: list[UUID] = []
        for chunk in chunks:
            content_lower = chunk.content.lower()
            if any(keyword in content_lower for keyword in keywords):
                evidence_ids.append(chunk.id)
        return evidence_ids
