"""Creamos las tablas necesarias para el chatbot

Revision ID: 2833c3af08de
Revises: c73490bf69b2
Create Date: 2025-07-02 13:28:28.274279

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2833c3af08de'
down_revision: Union[str, None] = 'c73490bf69b2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table('chat_conversations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('exercise_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['exercise_id'], ['ejercicios.id'], name='fk_chat_conversations_exercise_id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='fk_chat_conversations_user_id'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_chat_conversations_id'), 'chat_conversations', ['id'], unique=False)

    op.create_table('chat_messages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('conversation_id', sa.Integer(), nullable=False),
        sa.Column('sender_type', sa.String(), nullable=False),
        sa.Column('message', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['conversation_id'], ['chat_conversations.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_chat_messages_id'), 'chat_messages', ['id'], unique=False)

def downgrade():
    op.drop_index(op.f('ix_chat_messages_id'), table_name='chat_messages')
    op.drop_table('chat_messages')
    op.drop_index(op.f('ix_chat_conversations_id'), table_name='chat_conversations')
    op.drop_table('chat_conversations')
