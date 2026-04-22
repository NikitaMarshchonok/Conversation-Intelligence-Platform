from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.conversation import ConversationRead
from app.schemas.document import DocumentRead
from app.schemas.project import ProjectCreate, ProjectRead
from app.services.conversations_service import ConversationsService
from app.services.documents_service import DocumentsService
from app.services.projects_service import ProjectsService

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("", response_model=list[ProjectRead])
def list_projects(db: Session = Depends(get_db)) -> list[ProjectRead]:
    return ProjectsService.list_projects(db)


@router.post("", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
def create_project(payload: ProjectCreate, db: Session = Depends(get_db)) -> ProjectRead:
    return ProjectsService.create_project(db, payload)


@router.get("/{project_id}", response_model=ProjectRead)
def get_project(project_id: UUID, db: Session = Depends(get_db)) -> ProjectRead:
    project = ProjectsService.get_project_by_id(db, project_id)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return project


@router.post("/{project_id}/documents/upload", response_model=DocumentRead, status_code=status.HTTP_201_CREATED)
def upload_document(
    project_id: UUID,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> DocumentRead:
    try:
        return DocumentsService.create_uploaded_document(db, project_id, file)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get("/{project_id}/documents", response_model=list[DocumentRead])
def list_project_documents(project_id: UUID, db: Session = Depends(get_db)) -> list[DocumentRead]:
    project = ProjectsService.get_project_by_id(db, project_id)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return DocumentsService.list_project_documents(db, project_id)


@router.get("/{project_id}/conversations", response_model=list[ConversationRead])
def list_project_conversations(project_id: UUID, db: Session = Depends(get_db)) -> list[ConversationRead]:
    project = ProjectsService.get_project_by_id(db, project_id)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return ConversationsService.list_project_conversations(db, project_id)


@router.post("/{project_id}/conversations/upload", response_model=ConversationRead, status_code=status.HTTP_201_CREATED)
def upload_conversation_source(
    project_id: UUID,
    file: UploadFile = File(...),
    channel: str | None = Form(default=None),
    external_conversation_id: str | None = Form(default=None),
    title: str | None = Form(default=None),
    db: Session = Depends(get_db),
) -> ConversationRead:
    try:
        return ConversationsService.upload_conversation_source(
            db=db,
            project_id=project_id,
            upload=file,
            channel=channel,
            external_conversation_id=external_conversation_id,
            title=title,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
