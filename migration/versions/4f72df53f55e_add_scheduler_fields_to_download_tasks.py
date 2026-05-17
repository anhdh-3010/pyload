"""add scheduler fields to download tasks

Revision ID: 4f72df53f55e
Revises: 59f349a17810
Create Date: 2026-05-17 16:15:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "4f72df53f55e"
down_revision: str | Sequence[str] | None = "59f349a17810"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "download_tasks",
        sa.Column("locked_by", sa.String(length=128), nullable=True),
    )
    op.add_column(
        "download_tasks",
        sa.Column("locked_until", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "download_tasks",
        sa.Column(
            "attempts",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("0"),
        ),
    )
    op.add_column(
        "download_tasks",
        sa.Column(
            "max_attempts",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("3"),
        ),
    )
    op.add_column(
        "download_tasks",
        sa.Column(
            "run_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.create_index(
        "ix_download_tasks_scheduler_ready",
        "download_tasks",
        ["download_status", "run_at", "locked_until"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_download_tasks_scheduler_ready", table_name="download_tasks")
    op.drop_column("download_tasks", "run_at")
    op.drop_column("download_tasks", "max_attempts")
    op.drop_column("download_tasks", "attempts")
    op.drop_column("download_tasks", "locked_until")
    op.drop_column("download_tasks", "locked_by")
