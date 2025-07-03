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
    # La FK fue creada por 3bf9705971dd y se llama 'fk_temas_subject'
    op.drop_constraint(
        "fk_temas_subject",
        "temas",  # Tabla es 'temas' (plural)
        type_="foreignkey",
    )

    # 2. hacer la columna nullable
    op.alter_column(
        "temas",  # Tabla es 'temas' (plural)
        "subject_id",
        existing_type=sa.Integer(),
        nullable=True,
    )

    # 3. crear nueva FK con SET NULL
    op.create_foreign_key(
        "fk_temas_subject_set_null",  # Nuevo nombre para la FK con SET NULL
        "temas",  # Tabla es 'temas' (plural)
        "subjects",
        ["subject_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade():
    # revertir los pasos en orden inverso
    op.drop_constraint(
        "fk_temas_subject_set_null", # Dropear la FK creada en el upgrade
        "temas", # Tabla es 'temas' (plural)
        type_="foreignkey",
    )

    op.alter_column(
        "temas", # Tabla es 'temas' (plural)
        "subject_id",
        existing_type=sa.Integer(),
        nullable=False, # Volver a NOT NULL
    )

    # Recrear la FK original con ON DELETE CASCADE
    op.create_foreign_key(
        "fk_temas_subject", # Nombre original de la FK
        "temas", # Tabla es 'temas' (plural)
        "subjects",
        ["subject_id"],
        ["id"],
        ondelete="CASCADE",
    )
