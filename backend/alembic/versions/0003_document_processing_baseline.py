"""add document processing fields and chunks table

Revision ID: 0003_document_processing_baseline
Revises: 0002_document_upload_fields
Create Date: 2026-04-19 01:00:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "0003_document_processing_baseline"
down_revision: Union[str, None] = "0002_document_upload_fields"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("documents", sa.Column("processed_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("documents", sa.Column("processing_error", sa.String(length=2000), nullable=True))
    op.add_column("documents", sa.Column("chunk_count", sa.Integer(), server_default="0", nullable=False))

    op.create_table(
        "document_chunks",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("document_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("char_start", sa.Integer(), nullable=False),
        sa.Column("char_end", sa.Integer(), nullable=False),
        sa.Column("token_estimate", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_document_chunks_document_id"), "document_chunks", ["document_id"], unique=False)
    op.create_unique_constraint("uq_document_chunks_document_index", "document_chunks", ["document_id", "chunk_index"])


def downgrade() -> None:
    op.drop_constraint("uq_document_chunks_document_index", "document_chunks", type_="unique")
    op.drop_index(op.f("ix_document_chunks_document_id"), table_name="document_chunks")
    op.drop_table("document_chunks")

    op.drop_column("documents", "chunk_count")
    op.drop_column("documents", "processing_error")
    op.drop_column("documents", "processed_at")
