"""create user_enrollments table

Revision ID: b1c2d3e4f5a6
Revises: a09951c93e48
Create Date: 2025-05-11 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
# from sqlalchemy.dialects import postgresql # No parece necesario para esta tabla

# revision identifiers, used by Alembic.
revision: str = 'b1c2d3e4f5a6'
down_revision: Union[str, None] = 'a09951c93e48' # ID de la última migración conocida
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "user_enrollments",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("subject_id", sa.Integer(), nullable=False),
        sa.Column("course_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name="fk_user_enrollments_user_id", ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["subject_id"], ["subjects.id"], name="fk_user_enrollments_subject_id", ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["course_id"], ["courses.id"], name="fk_user_enrollments_course_id", ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("user_id", "subject_id", "course_id", name="pk_user_enrollments"),
        sa.UniqueConstraint("user_id", "subject_id", "course_id", name="uq_user_subject_course"),
    )


def downgrade() -> None:
    op.drop_table("user_enrollments")
