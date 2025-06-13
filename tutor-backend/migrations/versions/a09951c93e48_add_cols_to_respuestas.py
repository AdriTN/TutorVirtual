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
        "respuestas_usuarios",
        sa.Column("tiempo_seg", sa.Integer(), nullable=True)
    )
    op.add_column(
        "respuestas_usuarios",
        sa.Column(
            "respondida_en",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index(
        "ix_resp_user_ejercicio",
        "respuestas_usuarios",
        ["user_id", "ejercicio_id"],
        unique=True,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(
        "ix_resp_user_ejercicio", table_name="respuestas_usuarios"
    )
    op.drop_column("respuestas_usuarios", "respondida_en")
    op.drop_column("respuestas_usuarios", "tiempo_seg")
