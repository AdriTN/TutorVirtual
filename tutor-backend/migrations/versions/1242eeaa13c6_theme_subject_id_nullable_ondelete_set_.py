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
    # This migration's original purpose was to change themes.subject_id to nullable
    # and its FK to ON DELETE SET NULL.
    # However, migration 3bf9705971dd (as corrected) now sets up themes.subject_id
    # to be nullable=True with ON DELETE CASCADE, which matches the SQLAlchemy model.
    # Therefore, this migration is now a no-op to maintain model consistency.
    pass


def downgrade():
    # Since the upgrade is a no-op, the downgrade is also a no-op.
    # The previous state (matching the model) is maintained by 3bf9705971dd's downgrade.
    pass
