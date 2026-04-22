"""add conversation insights and compliance flags

Revision ID: 0007_conversation_analysis_baseline
Revises: 0006_ask_run_feedback
Create Date: 2026-04-19 03:00:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "0007_conversation_analysis_baseline"
down_revision: Union[str, None] = "0006_ask_run_feedback"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "conversation_insights",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("conversation_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("intent", sa.String(length=50), nullable=False),
        sa.Column("sentiment_label", sa.String(length=20), nullable=False),
        sa.Column("frustration_score", sa.Float(), nullable=False),
        sa.Column("evidence_chunk_ids", postgresql.ARRAY(postgresql.UUID(as_uuid=True)), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["conversation_id"], ["documents.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_conversation_insights_conversation_id"), "conversation_insights", ["conversation_id"], unique=True)

    op.create_table(
        "compliance_flags",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("conversation_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("flag_type", sa.String(length=100), nullable=False),
        sa.Column("is_triggered", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column("evidence_chunk_ids", postgresql.ARRAY(postgresql.UUID(as_uuid=True)), nullable=False),
        sa.Column("explanation", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["conversation_id"], ["documents.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_compliance_flags_conversation_id"), "compliance_flags", ["conversation_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_compliance_flags_conversation_id"), table_name="compliance_flags")
    op.drop_table("compliance_flags")
    op.drop_index(op.f("ix_conversation_insights_conversation_id"), table_name="conversation_insights")
    op.drop_table("conversation_insights")
