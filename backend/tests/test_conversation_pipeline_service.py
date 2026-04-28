from uuid import uuid4

import pytest

from app.services.conversation_pipeline_service import ConversationPipelineService
from app.services.document_indexing_service import DocumentIndexingService
from app.services.document_processing_service import DocumentProcessingService


def test_process_conversation_delegates_with_db_backed_lookup(
    real_db_session,
    db_conversation_with_document,
    monkeypatch,
) -> None:
    context = db_conversation_with_document
    called: dict = {}

    def _fake_process_document(*, db, document_id):
        called["db"] = db
        called["document_id"] = document_id
        context.document.status = "processed"
        context.document.chunk_count = 4
        return context.document

    monkeypatch.setattr(DocumentProcessingService, "process_document", _fake_process_document)

    response = ConversationPipelineService.process_conversation(
        db=real_db_session,
        conversation_id=context.conversation.id,
    )

    assert response.conversation_id == context.conversation.id
    assert response.document_id == context.document.id
    assert response.action == "process"
    assert response.document_status == "processed"
    assert response.chunk_count == 4
    assert called["db"] is real_db_session
    assert called["document_id"] == context.document.id


def test_index_conversation_delegates_with_db_backed_lookup(
    real_db_session,
    db_conversation_with_document,
    monkeypatch,
) -> None:
    context = db_conversation_with_document
    called: dict = {}

    def _fake_index_document(*, db, document_id):
        called["db"] = db
        called["document_id"] = document_id
        context.document.status = "processed"
        context.document.is_indexed = True
        return context.document

    monkeypatch.setattr(DocumentIndexingService, "index_document", _fake_index_document)

    response = ConversationPipelineService.index_conversation(
        db=real_db_session,
        conversation_id=context.conversation.id,
    )

    assert response.conversation_id == context.conversation.id
    assert response.document_id == context.document.id
    assert response.action == "index"
    assert response.document_status == "processed"
    assert response.is_indexed is True
    assert called["db"] is real_db_session
    assert called["document_id"] == context.document.id


def test_reindex_conversation_delegates_with_db_backed_lookup(
    real_db_session,
    db_conversation_with_document,
    monkeypatch,
) -> None:
    context = db_conversation_with_document
    called: dict = {}

    def _fake_reindex_document(*, db, document_id):
        called["db"] = db
        called["document_id"] = document_id
        context.document.status = "processed"
        context.document.is_indexed = True
        return context.document

    monkeypatch.setattr(DocumentIndexingService, "reindex_document", _fake_reindex_document)

    response = ConversationPipelineService.reindex_conversation(
        db=real_db_session,
        conversation_id=context.conversation.id,
    )

    assert response.conversation_id == context.conversation.id
    assert response.document_id == context.document.id
    assert response.action == "reindex"
    assert response.document_status == "processed"
    assert response.is_indexed is True
    assert called["db"] is real_db_session
    assert called["document_id"] == context.document.id


def test_process_conversation_raises_clean_error_when_conversation_missing(real_db_session) -> None:
    with pytest.raises(ValueError, match="Conversation not found"):
        ConversationPipelineService.process_conversation(db=real_db_session, conversation_id=uuid4())


def test_process_conversation_raises_clean_error_when_document_link_missing(
    real_db_session,
    db_conversation_without_document,
) -> None:
    with pytest.raises(ValueError, match="Conversation has no linked document"):
        ConversationPipelineService.process_conversation(
            db=real_db_session,
            conversation_id=db_conversation_without_document.conversation.id,
        )


def test_index_conversation_surfaces_indexing_precondition_failure_cleanly(
    real_db_session,
    db_conversation_with_document,
    monkeypatch,
) -> None:
    context = db_conversation_with_document

    def _raise_indexing_error(*, db, document_id):
        _ = (db, document_id)
        raise ValueError("Document must be processed before indexing")

    monkeypatch.setattr(DocumentIndexingService, "index_document", _raise_indexing_error)

    with pytest.raises(ValueError, match="Document must be processed before indexing"):
        ConversationPipelineService.index_conversation(
            db=real_db_session,
            conversation_id=context.conversation.id,
        )
