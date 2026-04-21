from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.ask_run import AskRunListItemRead, AskRunRead
from app.services.ask_runs_service import AskRunsService

router = APIRouter(prefix="/ask-runs", tags=["ask-runs"])


@router.get("", response_model=list[AskRunListItemRead])
def list_ask_runs(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    project_id: UUID | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[AskRunListItemRead]:
    return AskRunsService.list_ask_runs(
        db=db,
        offset=offset,
        limit=limit,
        project_id=project_id,
    )


@router.get("/{ask_run_id}", response_model=AskRunRead)
def get_ask_run(ask_run_id: UUID, db: Session = Depends(get_db)) -> AskRunRead:
    ask_run = AskRunsService.get_ask_run_by_id(db=db, ask_run_id=ask_run_id)
    if ask_run is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ask run not found")
    return ask_run
