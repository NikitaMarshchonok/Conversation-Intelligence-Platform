from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.metrics import QAMetricsResponse
from app.services.qa_metrics_service import QAMetricsService

router = APIRouter(prefix="/metrics", tags=["metrics"])


@router.get("/qa", response_model=QAMetricsResponse)
def get_qa_metrics(
    project_id: UUID | None = Query(default=None),
    start_date: datetime | None = Query(default=None),
    end_date: datetime | None = Query(default=None),
    db: Session = Depends(get_db),
) -> QAMetricsResponse:
    return QAMetricsService.get_qa_metrics(
        db=db,
        project_id=project_id,
        start_date=start_date,
        end_date=end_date,
    )
