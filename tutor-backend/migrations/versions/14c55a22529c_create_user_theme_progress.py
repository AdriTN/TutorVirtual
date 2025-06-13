"""create user_theme_progress

Revision ID: 14c55a22529c
Revises: a09951c93e48
Create Date: 2025-06-12 11:29:15.639987

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '14c55a22529c'
down_revision: Union[str, None] = 'a09951c93e48'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "user_theme_progress",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("tema_id", sa.Integer(), nullable=False),
        sa.Column("completed", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("correct", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["tema_id"], ["temas.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("user_id", "tema_id"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("user_theme_progress")
    