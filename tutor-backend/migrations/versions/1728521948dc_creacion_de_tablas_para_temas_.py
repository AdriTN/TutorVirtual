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
    # Crear la tabla de 'temas'
    op.create_table(
        'temas',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('nombre', sa.String(length=255), nullable=False, unique=True),
        sa.Column('descripcion', sa.Text(), nullable=True)
    )

    # Crear la tabla de 'ejercicios'
    op.create_table(
        'ejercicios',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('enunciado', sa.Text(), nullable=False),
        sa.Column('tipo', sa.String(length=50), nullable=False),  # suma, resta, multiplicación, etc.
        sa.Column('dificultad', sa.String(length=50), nullable=False),  # fácil, intermedio, difícil
        sa.Column('tema_id', sa.Integer(), sa.ForeignKey('temas.id', ondelete='CASCADE'), nullable=False)
    )

    # Crear la tabla de 'respuestas_usuarios'
    op.create_table(
        'respuestas_usuarios',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('respuesta', sa.Text(), nullable=False),
        sa.Column('ejercicio_id', sa.Integer(), sa.ForeignKey('ejercicios.id', ondelete='CASCADE'), nullable=False),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('correcto', sa.Boolean(), nullable=False)  # Indica si la respuesta es correcta o no
    )

    # Crear relaciones en las tablas
    op.create_foreign_key(
        'fk_respuestas_usuarios_user',
        'respuestas_usuarios', 'users',
        ['user_id'], ['id'], ondelete='CASCADE'
    )
    op.create_foreign_key(
        'fk_respuestas_usuarios_ejercicio',
        'respuestas_usuarios', 'ejercicios',
        ['ejercicio_id'], ['id'], ondelete='CASCADE'
    )
    op.create_foreign_key(
        'fk_ejercicios_tema',
        'ejercicios', 'temas',
        ['tema_id'], ['id'], ondelete='CASCADE'
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Eliminar en orden inverso de creación y dependencia
    # Las FKs explícitas creadas en upgrade() que no son parte de la definición de tabla
    # se eliminan aquí si es necesario, o se confía en que se eliminen con las tablas.
    # En este caso, las FKs fk_respuestas_usuarios_user, etc. se eliminan con las tablas.
    
    op.drop_table('respuestas_usuarios')
    op.drop_table('ejercicios')
    op.drop_table('temas')
    # ### end Alembic commands ###
