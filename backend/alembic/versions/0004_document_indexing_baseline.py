"""add document indexing metadata fields

Revision ID: 0004_document_indexing_baseline
Revises: 0003_document_processing_baseline
Create Date: 2026-04-19 01:30:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0004_document_indexing_baseline"
down_revision: Union[str, None] = "0003_document_processing_baseline"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("documents", sa.Column("indexed_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("documents", sa.Column("indexing_error", sa.String(length=2000), nullable=True))
    op.add_column("documents", sa.Column("is_indexed", sa.Boolean(), server_default=sa.false(), nullable=False))


def downgrade() -> None:
    op.drop_column("documents", "is_indexed")
    op.drop_column("documents", "indexing_error")
    op.drop_column("documents", "indexed_at")
