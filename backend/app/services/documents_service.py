import shutil
import uuid
from pathlib import Path
from uuid import UUID

from fastapi import UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.document import Document
from app.models.project import Project

settings = get_settings()


class DocumentsService:
    @staticmethod
    def get_storage_directory() -> Path:
        storage_dir = Path(settings.upload_storage_dir)
        storage_dir.mkdir(parents=True, exist_ok=True)
        return storage_dir

    @staticmethod
    def list_project_documents(db: Session, project_id: UUID) -> list[Document]:
        stmt = select(Document).where(Document.project_id == project_id).order_by(Document.created_at.desc())
        return list(db.scalars(stmt).all())

    @staticmethod
    def get_document_by_id(db: Session, document_id: UUID) -> Document | None:
        stmt = select(Document).where(Document.id == document_id)
        return db.scalar(stmt)

    @staticmethod
    def create_uploaded_document(db: Session, project_id: UUID, upload: UploadFile) -> Document:
        project = db.get(Project, project_id)
        if project is None:
            raise ValueError("Project not found")

        storage_dir = DocumentsService.get_storage_directory()
        extension = Path(upload.filename or "").suffix
        generated_name = f"{uuid.uuid4()}{extension}" if extension else str(uuid.uuid4())
        absolute_storage_path = storage_dir / generated_name

        with absolute_storage_path.open("wb") as destination:
            shutil.copyfileobj(upload.file, destination)

        stored_size = absolute_storage_path.stat().st_size
        relative_storage_path = absolute_storage_path.as_posix()
        document = Document(
            project_id=project_id,
            filename=generated_name,
            original_name=upload.filename or generated_name,
            mime_type=upload.content_type,
            size_bytes=stored_size,
            storage_path=relative_storage_path,
            status="uploaded",
        )
        db.add(document)
        db.commit()
        db.refresh(document)
        return document
