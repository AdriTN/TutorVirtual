"""add cols to respuestas

Revision ID: a09951c93e48
Revises: 0d4a3360c564
Create Date: 2025-06-12 11:28:23.224393

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'a09951c93e48'
down_revision: Union[str, None] = '0d4a3360c564'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "user_responses",  # Renamed
        sa.Column("time_sec", sa.Integer(), nullable=True)  # Renamed
    )
    op.add_column(
        "user_responses",  # Renamed
        sa.Column(
            "created_at",  # Renamed
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index(
        "uq_user_exercise",  # Renamed to match model's UniqueConstraint name
        "user_responses",    # Renamed
        ["user_id", "exercise_id"],  # Renamed column
        unique=True,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(
        "uq_user_exercise", table_name="user_responses"  # Renamed
    )
    op.drop_column("user_responses", "created_at")  # Renamed
    op.drop_column("user_responses", "time_sec")    # Renamed
