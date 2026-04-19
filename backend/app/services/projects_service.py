from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.project import Project
from app.schemas.project import ProjectCreate


class ProjectsService:
    @staticmethod
    def list_projects(db: Session) -> list[Project]:
        stmt = select(Project).order_by(Project.created_at.desc())
        return list(db.scalars(stmt).all())

    @staticmethod
    def get_project_by_id(db: Session, project_id: UUID) -> Project | None:
        stmt = select(Project).where(Project.id == project_id)
        return db.scalar(stmt)

    @staticmethod
    def create_project(db: Session, payload: ProjectCreate) -> Project:
        project = Project(name=payload.name.strip(), description=payload.description)
        db.add(project)
        db.commit()
        db.refresh(project)
        return project
