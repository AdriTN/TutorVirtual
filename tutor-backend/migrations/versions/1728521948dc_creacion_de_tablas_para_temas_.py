"""Creación de tablas para temas, ejercicios y respuestas

Revision ID: 1728521948dc
Revises: 41aa789df91c
Create Date: 2025-05-10 19:44:43.575843

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '1728521948dc'
down_revision: Union[str, None] = '41aa789df91c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create the 'themes' table
    op.create_table(
        'themes',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('name', sa.String(length=255), nullable=False, unique=True, index=True),
        sa.Column('description', sa.Text(), nullable=True)
    )
    op.create_index(op.f('ix_themes_name'), 'themes', ['name'], unique=True)

    # Create the 'exercises' table
    op.create_table(
        'exercises',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('statement', sa.Text(), nullable=False),
        sa.Column('type', sa.String(length=50), nullable=False),
        sa.Column('difficulty', sa.String(length=50), nullable=False),
        sa.Column('theme_id', sa.Integer(), sa.ForeignKey('themes.id', ondelete='CASCADE'), nullable=False)
    )

    # Create the 'user_responses' table
    op.create_table(
        'user_responses',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('answer', sa.Text(), nullable=False),
        sa.Column('exercise_id', sa.Integer(), sa.ForeignKey('exercises.id', ondelete='CASCADE'), nullable=False),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('correct', sa.Boolean(), nullable=False)
    )

    # Create foreign keys (adjusting names)
    # Note: SQLAlchemy's autogenerate often creates FKs directly in create_table.
    # Explicit create_foreign_key calls here are fine if they match what models imply or for clarity.
    # However, the ForeignKey() in Column definition already creates the constraint.
    # These explicit calls might be redundant if the inline FKs are named or if Alembic generates names.
    # For now, let's assume these explicit calls are for specific naming or ensuring they exist.
    # The original migration had these explicit calls.
    
    # FK for user_responses.user_id is implicitly created by ForeignKey('users.id')
    # op.create_foreign_key(
    # 'fk_user_responses_user', # Renamed
    # 'user_responses', 'users',
    #     ['user_id'], ['id'], ondelete='CASCADE'
    # )
    # FK for user_responses.exercise_id is implicitly created by ForeignKey('exercises.id')
    # op.create_foreign_key(
    # 'fk_user_responses_exercise', # Renamed
    # 'user_responses', 'exercises',
    #     ['exercise_id'], ['id'], ondelete='CASCADE'
    # )
    # FK for exercises.theme_id is implicitly created by ForeignKey('themes.id')
    # op.create_foreign_key(
    # 'fk_exercises_theme', # Renamed
    # 'exercises', 'themes',
    #     ['theme_id'], ['id'], ondelete='CASCADE'
    # )


def downgrade() -> None:
    """Downgrade schema."""
    # Drop in reverse order of creation
    op.drop_table('user_responses')
    op.drop_table('exercises')
    op.drop_index(op.f('ix_themes_name'), table_name='themes')
    op.drop_table('themes')
    # ### end Alembic commands ###
