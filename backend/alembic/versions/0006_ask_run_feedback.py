"""add ask run feedback table

Revision ID: 0006_ask_run_feedback
Revises: 0005_ask_run_persistence
Create Date: 2026-04-19 02:30:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "0006_ask_run_feedback"
down_revision: Union[str, None] = "0005_ask_run_persistence"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "ask_run_feedback",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("ask_run_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("rating", sa.Integer(), nullable=False),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["ask_run_id"], ["ask_runs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_ask_run_feedback_ask_run_id"), "ask_run_feedback", ["ask_run_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_ask_run_feedback_ask_run_id"), table_name="ask_run_feedback")
    op.drop_table("ask_run_feedback")
