from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.conversation import ConversationRead
from app.schemas.conversation_analysis import ConversationAnalyzeRequest, ConversationAnalyzeResponse
from app.services.conversation_analysis_service import ConversationAnalysisService
from app.services.conversations_service import ConversationsService

router = APIRouter(prefix="/conversations", tags=["conversations"])


@router.get("/{conversation_id}", response_model=ConversationRead)
def get_conversation(conversation_id: UUID, db: Session = Depends(get_db)) -> ConversationRead:
    conversation = ConversationsService.get_conversation_by_id(db, conversation_id)
    if conversation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    return conversation


@router.post("/{conversation_id}/analyze", response_model=ConversationAnalyzeResponse)
def analyze_conversation(
    conversation_id: UUID,
    payload: ConversationAnalyzeRequest,
    db: Session = Depends(get_db),
) -> ConversationAnalyzeResponse:
    try:
        return ConversationAnalysisService.analyze_conversation(
            db=db,
            conversation_id=conversation_id,
            payload=payload,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
