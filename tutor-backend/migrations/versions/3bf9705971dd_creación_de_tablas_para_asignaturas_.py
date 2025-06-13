"""Creación de relaciones faltantes

Revision ID: 3bf9705971dd
Revises: 1728521948dc
Create Date: 2025-05-14 11:30:27.288718
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# ──────────────────────────────────────────────────────────────────────────────
revision: str = "3bf9705971dd"
down_revision: Union[str, None] = "1728521948dc"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None
# ──────────────────────────────────────────────────────────────────────────────


def upgrade() -> None:
    """Añade subject_id a temas y crea las FKs que faltan"""

    # ─── 1. temas.subject_id  ────────────────────────────────────────────────
    op.add_column(
        "temas",
        sa.Column("subject_id", sa.Integer(), nullable=False),
    )
    op.create_foreign_key(
        "fk_temas_subject",
        "temas",
        "subjects",
        ["subject_id"],
        ["id"],
        ondelete="CASCADE",
    )

    # ─── 3. FKs en respuestas_usuarios  (columnas ya existen) ────────────────
    op.create_foreign_key(
        "fk_respuestas_user",
        "respuestas_usuarios",
        "users",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "fk_respuestas_ejercicio",
        "respuestas_usuarios",
        "ejercicios",
        ["ejercicio_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    """Revierte los cambios anteriores"""

    # FKs de respuestas_usuarios
    op.drop_constraint("fk_respuestas_ejercicio", "respuestas_usuarios", type_="foreignkey")
    op.drop_constraint("fk_respuestas_user", "respuestas_usuarios", type_="foreignkey")

    # FK de ejercicios.tema_id
    op.drop_constraint("fk_ejercicios_tema", "ejercicios", type_="foreignkey")

    # Columna y FK de temas.subject_id
    op.drop_constraint("fk_temas_subject", "temas", type_="foreignkey")
    op.drop_column("temas", "subject_id")
