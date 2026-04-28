from collections.abc import Generator
from dataclasses import dataclass
from pathlib import Path
import sys
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import app.models  # noqa: F401 - ensure model metadata is registered for test tables
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models.conversation import Conversation
from app.models.document import Document
from app.models.project import Project


class DummySession:
    """Minimal DB session placeholder for route dependency overrides."""


@dataclass(frozen=True)
class SampleConversationContext:
    project_id: UUID
    conversation_id: UUID
    document_id: UUID | None


@dataclass(frozen=True)
class DbConversationContext:
    project: Project
    document: Document | None
    conversation: Conversation


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


@pytest.fixture
def real_db_session(tmp_path) -> Generator[Session, None, None]:
    db_file = tmp_path / "service-tests.db"
    engine = create_engine(f"sqlite+pysqlite:///{db_file}", future=True)

    @event.listens_for(engine, "connect")
    def _set_sqlite_pragma(dbapi_connection, connection_record) -> None:  # noqa: ARG001
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    required_tables = [Project.__table__, Document.__table__, Conversation.__table__]
    Base.metadata.create_all(bind=engine, tables=required_tables)
    session_local = sessionmaker(bind=engine, autocommit=False, autoflush=False, class_=Session)
    session = session_local()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine, tables=required_tables)
        engine.dispose()


@pytest.fixture
def db_conversation_with_document(real_db_session: Session) -> DbConversationContext:
    project = Project(name=f"svc-project-{uuid4()}", description="service test project")
    real_db_session.add(project)
    real_db_session.flush()

    document = Document(
        project_id=project.id,
        filename="conversation.txt",
        original_name="conversation.txt",
        mime_type="text/plain",
        size_bytes=32,
        storage_path=f"/tmp/{uuid4()}-conversation.txt",
        status="uploaded",
        chunk_count=0,
        is_indexed=False,
    )
    real_db_session.add(document)
    real_db_session.flush()

    conversation = Conversation(
        project_id=project.id,
        document_id=document.id,
        channel="chat",
        title="Service Test Conversation",
        status="active",
    )
    real_db_session.add(conversation)
    real_db_session.commit()
    real_db_session.refresh(project)
    real_db_session.refresh(document)
    real_db_session.refresh(conversation)

    return DbConversationContext(project=project, document=document, conversation=conversation)


@pytest.fixture
def db_conversation_without_document(real_db_session: Session) -> DbConversationContext:
    project = Project(name=f"svc-project-{uuid4()}", description="service test project no document")
    real_db_session.add(project)
    real_db_session.flush()

    conversation = Conversation(
        project_id=project.id,
        document_id=None,
        channel="chat",
        title="Service Test Conversation No Document",
        status="active",
    )
    real_db_session.add(conversation)
    real_db_session.commit()
    real_db_session.refresh(project)
    real_db_session.refresh(conversation)

    return DbConversationContext(project=project, document=None, conversation=conversation)
