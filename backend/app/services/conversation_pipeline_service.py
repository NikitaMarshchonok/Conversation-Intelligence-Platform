from uuid import UUID

from sqlalchemy.orm import Session

from app.models.document import Document
from app.schemas.conversation import ConversationPipelineActionResponse
from app.services.conversations_service import ConversationsService
from app.services.document_indexing_service import DocumentIndexingService
from app.services.document_processing_service import DocumentProcessingService


class ConversationPipelineService:
    @staticmethod
    def process_conversation(db: Session, conversation_id: UUID) -> ConversationPipelineActionResponse:
        document = ConversationPipelineService._get_linked_document(db, conversation_id)
        processed = DocumentProcessingService.process_document(db=db, document_id=document.id)
        return ConversationPipelineService._build_response(
            conversation_id=conversation_id,
            document=processed,
            action="process",
        )

    @staticmethod
    def index_conversation(db: Session, conversation_id: UUID) -> ConversationPipelineActionResponse:
        document = ConversationPipelineService._get_linked_document(db, conversation_id)
        indexed = DocumentIndexingService.index_document(db=db, document_id=document.id)
        return ConversationPipelineService._build_response(
            conversation_id=conversation_id,
            document=indexed,
            action="index",
        )

    @staticmethod
    def reindex_conversation(db: Session, conversation_id: UUID) -> ConversationPipelineActionResponse:
        document = ConversationPipelineService._get_linked_document(db, conversation_id)
        indexed = DocumentIndexingService.reindex_document(db=db, document_id=document.id)
        return ConversationPipelineService._build_response(
            conversation_id=conversation_id,
            document=indexed,
            action="reindex",
        )

    @staticmethod
    def _get_linked_document(db: Session, conversation_id: UUID) -> Document:
        conversation = ConversationsService.get_conversation_by_id(db=db, conversation_id=conversation_id)
        if conversation is None:
            raise ValueError("Conversation not found")
        if conversation.document_id is None:
            raise ValueError("Conversation has no linked document")
        document = db.get(Document, conversation.document_id)
        if document is None:
            raise ValueError("Linked document not found")
        return document

    @staticmethod
    def _build_response(
        conversation_id: UUID,
        document: Document,
        action: str,
    ) -> ConversationPipelineActionResponse:
        return ConversationPipelineActionResponse(
            conversation_id=conversation_id,
            document_id=document.id,
            action=action,
            document_status=document.status,
            chunk_count=document.chunk_count,
            processed_at=document.processed_at,
            processing_error=document.processing_error,
            is_indexed=document.is_indexed,
            indexed_at=document.indexed_at,
            indexing_error=document.indexing_error,
        )
