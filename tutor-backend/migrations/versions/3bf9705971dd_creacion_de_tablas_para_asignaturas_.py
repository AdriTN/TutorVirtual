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
    """Adds subject_id to themes table, matching the model (nullable=True, ondelete='CASCADE')"""

    # Add subject_id to themes table
    op.add_column(
        "themes",  # Renamed from "temas"
        sa.Column("subject_id", sa.Integer(), nullable=True),  # Model: nullable=True
    )
    op.create_foreign_key(
        "fk_themes_subject_id",  # Renamed FK constraint
        "themes",  # Source table
        "subjects",  # Target table
        ["subject_id"],  # Local columns
        ["id"],  # Remote columns
        ondelete="CASCADE",  # Model: ondelete="CASCADE"
    )

    # The following FK creations were redundant as they are established
    # by the initial create_table in 1728521948dc_*.py
    # ─── FKs en user_responses (columnas ya existen) ────────────────
    # op.create_foreign_key(
    #     "fk_user_responses_user_id",
    #     "user_responses",
    #     "users",
    #     ["user_id"],
    #     ["id"],
    #     ondelete="CASCADE",
    # )
    # op.create_foreign_key(
    #     "fk_user_responses_exercise_id",
    #     "user_responses",
    #     "exercises",
    #     ["exercise_id"],
    #     ["id"],
    #     ondelete="CASCADE",
    # )


def downgrade() -> None:
    """Reverts the changes made in the upgrade function"""

    # Drop column and FK for themes.subject_id
    op.drop_constraint("fk_themes_subject_id", "themes", type_="foreignkey")
    op.drop_column("themes", "subject_id")

    # Since the other FKs were not created in the upgrade,
    # no need to drop them here. They are handled by 1728521948dc_*.py's downgrade.
