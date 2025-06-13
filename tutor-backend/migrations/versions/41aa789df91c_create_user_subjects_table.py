"""create user_subjects table

Revision ID: 41aa789df91c
Revises: f313f70c3072
Create Date: 2025-05-06 18:43:30.365636

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '41aa789df91c'
down_revision: Union[str, None] = 'f313f70c3072'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "user_subjects",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("subject_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["subject_id"], ["subjects.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("user_id", "subject_id"),
        sa.UniqueConstraint("user_id", "subject_id", name="uq_user_subject"),
    )


def downgrade() -> None:
    op.drop_table("user_subjects")
