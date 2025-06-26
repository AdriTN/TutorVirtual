"""theme.subject_id nullable, ondelete SET NULL

Revision ID: 1242eeaa13c6
Revises: 14c55a22529c
Create Date: 2025-06-26 18:02:59.286310

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1242eeaa13c6'
down_revision: Union[str, None] = '14c55a22529c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # 1. quitar la FK antigua (CASCADE, NOT NULL)
    op.drop_constraint(
        "themes_subject_id_fkey",   # ← nombre real en tu BD
        "themes",
        type_="foreignkey",
    )

    # 2. hacer la columna nullable
    op.alter_column(
        "themes",
        "subject_id",
        existing_type=sa.Integer(),
        nullable=True,
    )

    # 3. crear nueva FK con SET NULL
    op.create_foreign_key(
        "themes_subject_id_fkey",    # mismo nombre u otro, pero único
        "themes",
        "subjects",
        ["subject_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade():
    # revertir los pasos en orden inverso
    op.drop_constraint(
        "themes_subject_id_fkey",
        "themes",
        type_="foreignkey",
    )

    op.alter_column(
        "themes",
        "subject_id",
        existing_type=sa.Integer(),
        nullable=False,
    )

    op.create_foreign_key(
        "themes_subject_id_fkey",
        "themes",
        "subjects",
        ["subject_id"],
        ["id"],
        ondelete="CASCADE",
    )
