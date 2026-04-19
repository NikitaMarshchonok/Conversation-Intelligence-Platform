"""add document upload metadata fields

Revision ID: 0002_document_upload_fields
Revises: 0001_initial
Create Date: 2026-04-19 00:30:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0002_document_upload_fields"
down_revision: Union[str, None] = "0001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("documents", sa.Column("original_name", sa.String(length=255), nullable=True))
    op.add_column("documents", sa.Column("mime_type", sa.String(length=255), nullable=True))
    op.add_column("documents", sa.Column("size_bytes", sa.BigInteger(), nullable=True))
    op.add_column("documents", sa.Column("storage_path", sa.String(length=1024), nullable=True))
    op.create_unique_constraint("uq_documents_storage_path", "documents", ["storage_path"])

    op.execute("UPDATE documents SET original_name = filename WHERE original_name IS NULL")
    op.execute("UPDATE documents SET size_bytes = 0 WHERE size_bytes IS NULL")
    op.execute("UPDATE documents SET storage_path = CONCAT('migrated/', id::text) WHERE storage_path IS NULL")

    op.alter_column("documents", "original_name", nullable=False)
    op.alter_column("documents", "size_bytes", nullable=False)
    op.alter_column("documents", "storage_path", nullable=False)

    op.drop_column("documents", "raw_text")


def downgrade() -> None:
    op.add_column("documents", sa.Column("raw_text", sa.Text(), nullable=True))
    op.drop_constraint("uq_documents_storage_path", "documents", type_="unique")
    op.drop_column("documents", "storage_path")
    op.drop_column("documents", "size_bytes")
    op.drop_column("documents", "mime_type")
    op.drop_column("documents", "original_name")
