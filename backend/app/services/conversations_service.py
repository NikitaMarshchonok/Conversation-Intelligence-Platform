from uuid import UUID

from fastapi import UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.conversation import Conversation
from app.models.document import Document
from app.services.documents_service import DocumentsService


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

    @staticmethod
    def upload_conversation_source(
        db: Session,
        project_id: UUID,
        upload: UploadFile,
        channel: str | None = None,
        external_conversation_id: str | None = None,
        title: str | None = None,
    ) -> Conversation:
        document = DocumentsService.create_uploaded_document(db=db, project_id=project_id, upload=upload)
        conversation = ConversationsService.get_or_create_by_document(db=db, document=document, force_id_as_document_id=True)

        if channel is not None and channel.strip():
            conversation.channel = channel.strip().lower()
        if external_conversation_id is not None and external_conversation_id.strip():
            conversation.external_conversation_id = external_conversation_id.strip()
        if title is not None and title.strip():
            conversation.title = title.strip()

        db.commit()
        db.refresh(conversation)
        return conversation
