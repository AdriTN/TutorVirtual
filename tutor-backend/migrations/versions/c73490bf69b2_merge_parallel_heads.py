"""merge parallel heads

Revision ID: c73490bf69b2
Revises: 8395b8397318, c2d3e4f5a6b7
Create Date: 2025-07-02 13:28:02.442679

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c73490bf69b2'
down_revision: Union[str, None] = ('8395b8397318', 'c2d3e4f5a6b7')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
