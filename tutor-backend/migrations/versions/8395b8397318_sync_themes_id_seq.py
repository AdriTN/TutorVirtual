"""sync themes_id_seq

Revision ID: 8395b8397318
Revises: 1242eeaa13c6
Create Date: 2025-06-26 18:14:09.843410

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8395b8397318'
down_revision: Union[str, None] = '1242eeaa13c6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.execute(sa.text("""
        SELECT setval(
            pg_get_serial_sequence('themes', 'id'),
            (SELECT COALESCE(MAX(id),0)+1 FROM themes),
            false
        );
    """))

def downgrade():
    pass
