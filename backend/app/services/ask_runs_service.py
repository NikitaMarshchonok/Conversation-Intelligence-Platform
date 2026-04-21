from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.ask_run import AskRun
from app.models.ask_run_citation import AskRunCitation
from app.schemas.ask import AskCitation


class AskRunsService:
    @staticmethod
    def create_ask_run(
        db: Session,
        project_id: UUID,
        query: str,
        answer: str,
        status: str,
        latency_ms: int,
        retrieved_chunk_ids: list[UUID],
        reranked_chunk_ids: list[UUID],
        cited_chunk_ids: list[UUID],
        citations: list[AskCitation],
    ) -> AskRun:
        ask_run = AskRun(
            project_id=project_id,
            query=query,
            answer=answer,
            status=status,
            latency_ms=latency_ms,
            retrieved_chunk_ids=retrieved_chunk_ids,
            reranked_chunk_ids=reranked_chunk_ids,
            cited_chunk_ids=cited_chunk_ids,
        )
        db.add(ask_run)
        db.flush()

        for index, citation in enumerate(citations):
            db.add(
                AskRunCitation(
                    ask_run_id=ask_run.id,
                    document_id=citation.document_id,
                    chunk_id=citation.chunk_id,
                    chunk_index=citation.chunk_index,
                    snippet=citation.snippet,
                    citation_order=index + 1,
                )
            )

        db.commit()
        db.refresh(ask_run)
        return ask_run

    @staticmethod
    def list_ask_runs(
        db: Session,
        offset: int,
        limit: int,
        project_id: UUID | None = None,
    ) -> list[AskRun]:
        stmt = select(AskRun).order_by(AskRun.created_at.desc()).offset(offset).limit(limit)
        if project_id is not None:
            stmt = stmt.where(AskRun.project_id == project_id)
        return list(db.scalars(stmt).all())

    @staticmethod
    def get_ask_run_by_id(db: Session, ask_run_id: UUID) -> AskRun | None:
        stmt = (
            select(AskRun)
            .where(AskRun.id == ask_run_id)
            .options(selectinload(AskRun.citations))
        )
        return db.scalar(stmt)
