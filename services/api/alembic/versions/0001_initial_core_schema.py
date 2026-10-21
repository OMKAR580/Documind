"""Initial core infrastructure schema

Revision ID: 0001_initial_core_schema
Revises:
Create Date: 2026-10-21 23:30:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0001_initial_core_schema"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "system_metadata",
        sa.Column("key", sa.String(length=128), nullable=False),
        sa.Column("value", sa.Text(), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.PrimaryKeyConstraint("key"),
    )
    op.create_index(op.f("ix_system_metadata_key"), "system_metadata", ["key"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_system_metadata_key"), table_name="system_metadata")
    op.drop_table("system_metadata")
