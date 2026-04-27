from collections.abc import Generator
from dataclasses import dataclass
from pathlib import Path
import sys
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.db.session import get_db
from app.main import app


class DummySession:
    """Minimal DB session placeholder for route dependency overrides."""


@dataclass(frozen=True)
class SampleConversationContext:
    project_id: UUID
    conversation_id: UUID
    document_id: UUID | None


@pytest.fixture
def db_session() -> DummySession:
    return DummySession()


@pytest.fixture
def client(db_session: DummySession) -> Generator[TestClient, None, None]:
    def _get_test_db() -> Generator[DummySession, None, None]:
        yield db_session

    app.dependency_overrides[get_db] = _get_test_db
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()


@pytest.fixture
def sample_conversation_with_document() -> SampleConversationContext:
    return SampleConversationContext(
        project_id=uuid4(),
        conversation_id=uuid4(),
        document_id=uuid4(),
    )


@pytest.fixture
def sample_conversation_without_document() -> SampleConversationContext:
    return SampleConversationContext(
        project_id=uuid4(),
        conversation_id=uuid4(),
        document_id=None,
    )
