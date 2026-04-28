"""report 테이블에 user_id, month_start, month_end 컬럼 추가

Revision ID: 001
Revises:
Create Date: 2026-04-28
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "001"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("report", sa.Column("user_id", sa.Integer(), nullable=True))
    op.add_column("report", sa.Column("month_start", sa.String(10), nullable=True))
    op.add_column("report", sa.Column("month_end", sa.String(10), nullable=True))


def downgrade() -> None:
    op.drop_column("report", "month_end")
    op.drop_column("report", "month_start")
    op.drop_column("report", "user_id")
