"""add conversations domain entity and bridge analysis tables

Revision ID: 0008_conversations_domain_baseline
Revises: 0007_conversation_analysis_baseline
Create Date: 2026-04-19 03:30:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "0008_conversations_domain_baseline"
down_revision: Union[str, None] = "0007_conversation_analysis_baseline"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "conversations",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("document_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("external_conversation_id", sa.String(length=255), nullable=True),
        sa.Column("channel", sa.String(length=20), server_default="unknown", nullable=False),
        sa.Column("title", sa.String(length=255), nullable=True),
        sa.Column("status", sa.String(length=50), server_default="active", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_conversations_project_id"), "conversations", ["project_id"], unique=False)
    op.create_index(op.f("ix_conversations_document_id"), "conversations", ["document_id"], unique=True)

    op.execute(
        """
        INSERT INTO conversations (id, project_id, document_id, channel, title, status, created_at, updated_at)
        SELECT d.id, d.project_id, d.id, 'unknown', d.original_name, 'active', d.created_at, d.updated_at
        FROM documents d
        ON CONFLICT (id) DO NOTHING
        """
    )

    op.add_column("conversation_insights", sa.Column("conversation_ref_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.create_foreign_key(
        "fk_conversation_insights_conversation_ref_id",
        "conversation_insights",
        "conversations",
        ["conversation_ref_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.execute("UPDATE conversation_insights SET conversation_ref_id = conversation_id")
    op.alter_column("conversation_insights", "conversation_ref_id", nullable=False)
    op.drop_index(op.f("ix_conversation_insights_conversation_id"), table_name="conversation_insights")
    op.drop_column("conversation_insights", "conversation_id")
    op.alter_column("conversation_insights", "conversation_ref_id", new_column_name="conversation_id")
    op.create_index(op.f("ix_conversation_insights_conversation_id"), "conversation_insights", ["conversation_id"], unique=True)

    op.add_column("compliance_flags", sa.Column("conversation_ref_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.create_foreign_key(
        "fk_compliance_flags_conversation_ref_id",
        "compliance_flags",
        "conversations",
        ["conversation_ref_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.execute("UPDATE compliance_flags SET conversation_ref_id = conversation_id")
    op.alter_column("compliance_flags", "conversation_ref_id", nullable=False)
    op.drop_index(op.f("ix_compliance_flags_conversation_id"), table_name="compliance_flags")
    op.drop_column("compliance_flags", "conversation_id")
    op.alter_column("compliance_flags", "conversation_ref_id", new_column_name="conversation_id")
    op.create_index(op.f("ix_compliance_flags_conversation_id"), "compliance_flags", ["conversation_id"], unique=False)


def downgrade() -> None:
    op.add_column("compliance_flags", sa.Column("document_ref_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.create_foreign_key(
        "fk_compliance_flags_document_ref_id",
        "compliance_flags",
        "documents",
        ["document_ref_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.execute(
        """
        UPDATE compliance_flags cf
        SET document_ref_id = c.document_id
        FROM conversations c
        WHERE cf.conversation_id = c.id
        """
    )
    op.alter_column("compliance_flags", "document_ref_id", nullable=False)
    op.drop_index(op.f("ix_compliance_flags_conversation_id"), table_name="compliance_flags")
    op.drop_column("compliance_flags", "conversation_id")
    op.alter_column("compliance_flags", "document_ref_id", new_column_name="conversation_id")
    op.create_index(op.f("ix_compliance_flags_conversation_id"), "compliance_flags", ["conversation_id"], unique=False)

    op.add_column("conversation_insights", sa.Column("document_ref_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.create_foreign_key(
        "fk_conversation_insights_document_ref_id",
        "conversation_insights",
        "documents",
        ["document_ref_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.execute(
        """
        UPDATE conversation_insights ci
        SET document_ref_id = c.document_id
        FROM conversations c
        WHERE ci.conversation_id = c.id
        """
    )
    op.alter_column("conversation_insights", "document_ref_id", nullable=False)
    op.drop_index(op.f("ix_conversation_insights_conversation_id"), table_name="conversation_insights")
    op.drop_column("conversation_insights", "conversation_id")
    op.alter_column("conversation_insights", "document_ref_id", new_column_name="conversation_id")
    op.create_index(op.f("ix_conversation_insights_conversation_id"), "conversation_insights", ["conversation_id"], unique=True)

    op.drop_index(op.f("ix_conversations_document_id"), table_name="conversations")
    op.drop_index(op.f("ix_conversations_project_id"), table_name="conversations")
    op.drop_table("conversations")
