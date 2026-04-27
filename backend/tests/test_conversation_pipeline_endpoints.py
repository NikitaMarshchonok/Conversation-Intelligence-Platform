from uuid import uuid4

import pytest

from app.schemas.conversation import ConversationPipelineActionResponse
from app.services.conversation_pipeline_service import ConversationPipelineService


def _build_payload(action: str) -> ConversationPipelineActionResponse:
    return ConversationPipelineActionResponse(
        conversation_id=uuid4(),
        document_id=uuid4(),
        action=action,
        document_status="processed",
        chunk_count=3,
        processed_at=None,
        processing_error=None,
        is_indexed=action in {"index", "reindex"},
        indexed_at=None,
        indexing_error=None,
    )


def _assert_common_response_shape(data: dict, expected_action: str) -> None:
    assert data["conversation_id"]
    assert data["document_id"]
    assert data["action"] == expected_action
    assert "document_status" in data
    assert "chunk_count" in data
    assert "processed_at" in data
    assert "processing_error" in data
    assert "is_indexed" in data
    assert "indexed_at" in data
    assert "indexing_error" in data


def test_process_conversation_success_returns_conversation_oriented_payload(client, db_session, monkeypatch) -> None:
    response_payload = _build_payload(action="process")
    called: dict = {}

    def _fake_process_conversation(*, db, conversation_id):
        called["db"] = db
        called["conversation_id"] = conversation_id
        return response_payload

    monkeypatch.setattr(ConversationPipelineService, "process_conversation", _fake_process_conversation)
    target_conversation_id = uuid4()

    response = client.post(f"/conversations/{target_conversation_id}/process")

    assert response.status_code == 200
    data = response.json()
    _assert_common_response_shape(data, expected_action="process")
    assert called["db"] is db_session
    assert called["conversation_id"] == target_conversation_id


def test_index_conversation_success_returns_conversation_oriented_payload(client, db_session, monkeypatch) -> None:
    response_payload = _build_payload(action="index")
    called: dict = {}

    def _fake_index_conversation(*, db, conversation_id):
        called["db"] = db
        called["conversation_id"] = conversation_id
        return response_payload

    monkeypatch.setattr(ConversationPipelineService, "index_conversation", _fake_index_conversation)
    target_conversation_id = uuid4()

    response = client.post(f"/conversations/{target_conversation_id}/index")

    assert response.status_code == 200
    data = response.json()
    _assert_common_response_shape(data, expected_action="index")
    assert data["is_indexed"] is True
    assert called["db"] is db_session
    assert called["conversation_id"] == target_conversation_id


def test_reindex_conversation_success_returns_conversation_oriented_payload(client, db_session, monkeypatch) -> None:
    response_payload = _build_payload(action="reindex")
    called: dict = {}

    def _fake_reindex_conversation(*, db, conversation_id):
        called["db"] = db
        called["conversation_id"] = conversation_id
        return response_payload

    monkeypatch.setattr(ConversationPipelineService, "reindex_conversation", _fake_reindex_conversation)
    target_conversation_id = uuid4()

    response = client.post(f"/conversations/{target_conversation_id}/reindex")

    assert response.status_code == 200
    data = response.json()
    _assert_common_response_shape(data, expected_action="reindex")
    assert data["is_indexed"] is True
    assert called["db"] is db_session
    assert called["conversation_id"] == target_conversation_id


@pytest.mark.parametrize(
    ("path_suffix", "service_method", "error_message"),
    [
        ("process", "process_conversation", "Conversation not found"),
        ("process", "process_conversation", "Conversation has no linked document"),
        ("index", "index_conversation", "Document must be processed before indexing"),
    ],
)
def test_proxy_endpoints_return_clean_400_for_expected_pipeline_failures(
    client,
    monkeypatch,
    path_suffix: str,
    service_method: str,
    error_message: str,
) -> None:
    def _raise_value_error(*, db, conversation_id):
        _ = (db, conversation_id)
        raise ValueError(error_message)

    monkeypatch.setattr(ConversationPipelineService, service_method, _raise_value_error)
    conversation_id = uuid4()

    response = client.post(f"/conversations/{conversation_id}/{path_suffix}")

    assert response.status_code == 400
    assert response.json() == {"detail": error_message}
