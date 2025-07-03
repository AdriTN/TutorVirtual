"""add cols to ejercicios

Revision ID: 0d4a3360c564
Revises: 3bf9705971dd
Create Date: 2025-06-12 11:25:16.622511

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '0d4a3360c564'
down_revision: Union[str, None] = '3bf9705971dd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "exercises",  # Renamed from "ejercicios"
        sa.Column("answer", sa.Text(), nullable=False)  # Renamed, removed server_default
    )
    op.add_column(
        "exercises",  # Renamed from "ejercicios"
        sa.Column("explanation", sa.Text(), nullable=True)  # Renamed
    )
    op.add_column(
        "exercises",  # Renamed from "ejercicios"
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index("ix_exercises_theme_id", "exercises", ["theme_id"]) # Renamed index and column


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("ix_exercises_theme_id", table_name="exercises") # Dropping renamed index
    op.drop_column("exercises", "created_at")
    op.drop_column("exercises", "explanation") # Renamed
    op.drop_column("exercises", "answer")      # Renamed
    # ### end Alembic commands ###
