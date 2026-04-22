from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.conversation import Conversation
from app.models.document import Document


class ConversationsService:
    @staticmethod
    def list_project_conversations(db: Session, project_id: UUID) -> list[Conversation]:
        stmt = select(Conversation).where(Conversation.project_id == project_id).order_by(Conversation.created_at.desc())
        return list(db.scalars(stmt).all())

    @staticmethod
    def get_conversation_by_id(db: Session, conversation_id: UUID) -> Conversation | None:
        stmt = select(Conversation).where(Conversation.id == conversation_id)
        return db.scalar(stmt)

    @staticmethod
    def get_or_create_by_document(db: Session, document: Document, force_id_as_document_id: bool = False) -> Conversation:
        existing_stmt = select(Conversation).where(Conversation.document_id == document.id)
        existing = db.scalar(existing_stmt)
        if existing is not None:
            return existing

        conversation_kwargs = {
            "project_id": document.project_id,
            "document_id": document.id,
            "channel": "unknown",
            "title": document.original_name,
            "status": "active",
        }
        if force_id_as_document_id:
            conversation_kwargs["id"] = document.id
        conversation = Conversation(**conversation_kwargs)
        db.add(conversation)
        db.flush()
        return conversation
