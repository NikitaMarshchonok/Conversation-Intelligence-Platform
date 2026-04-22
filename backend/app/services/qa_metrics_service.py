from datetime import datetime
from uuid import UUID

from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from app.models.ask_run import AskRun
from app.models.ask_run_feedback import AskRunFeedback
from app.schemas.metrics import QAMetricsResponse


class QAMetricsService:
    @staticmethod
    def get_qa_metrics(
        db: Session,
        project_id: UUID | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> QAMetricsResponse:
        ask_run_stmt = select(
            func.count(AskRun.id),
            func.sum(case((AskRun.status == "failed", 1), else_=0)),
            func.avg(AskRun.latency_ms),
        )
        ask_run_stmt = QAMetricsService._apply_ask_run_filters(
            stmt=ask_run_stmt,
            project_id=project_id,
            start_date=start_date,
            end_date=end_date,
        )
        total_ask_runs, failed_ask_runs, avg_latency_ms = db.execute(ask_run_stmt).one()

        feedback_stmt = (
            select(
                func.count(AskRunFeedback.id),
                func.avg(AskRunFeedback.rating),
            )
            .select_from(AskRunFeedback)
            .join(AskRun, AskRun.id == AskRunFeedback.ask_run_id)
        )
        feedback_stmt = QAMetricsService._apply_ask_run_filters(
            stmt=feedback_stmt,
            project_id=project_id,
            start_date=start_date,
            end_date=end_date,
        )
        feedback_count, avg_rating = db.execute(feedback_stmt).one()

        return QAMetricsResponse(
            total_ask_runs=int(total_ask_runs or 0),
            failed_ask_runs=int(failed_ask_runs or 0),
            avg_latency_ms=float(avg_latency_ms or 0.0),
            feedback_count=int(feedback_count or 0),
            avg_rating=float(avg_rating or 0.0),
        )

    @staticmethod
    def _apply_ask_run_filters(stmt, project_id: UUID | None, start_date: datetime | None, end_date: datetime | None):
        if project_id is not None:
            stmt = stmt.where(AskRun.project_id == project_id)
        if start_date is not None:
            stmt = stmt.where(AskRun.created_at >= start_date)
        if end_date is not None:
            stmt = stmt.where(AskRun.created_at <= end_date)
        return stmt
