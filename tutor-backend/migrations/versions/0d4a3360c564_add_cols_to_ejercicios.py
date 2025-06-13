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
        "ejercicios",
        sa.Column("respuesta", sa.Text(), nullable=False, server_default="")
    )
    op.add_column(
        "ejercicios",
        sa.Column("explicacion", sa.Text(), nullable=True)
    )
    op.add_column(
        "ejercicios",
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index("ix_ejercicio_tema", "ejercicios", ["tema_id"])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("ejercicios", "created_at")
    op.drop_column("ejercicios", "explicacion")
    op.drop_column("ejercicios", "respuesta")
    # ### end Alembic commands ###
