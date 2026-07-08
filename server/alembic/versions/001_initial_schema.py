"""initial schema

Revision ID: 001
Revises: 
Create Date: 2026-07-07 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from pgvector.sqlalchemy import Vector as pgvector_Vector

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create users table
    op.create_table('users',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), primary_key=True),
        sa.Column('provider', sa.Text(), nullable=False),
        sa.Column('provider_id', sa.Text(), nullable=False, index=True),
        sa.Column('display_name', sa.Text(), nullable=False),
        sa.Column('email', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('last_seen_at', sa.DateTime(timezone=True), nullable=True),
    )

    # Create memories table
    op.create_table('memories',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), primary_key=True),
        sa.Column('name', sa.Text(), nullable=False),
        sa.Column('type', sa.Text(), server_default='project', nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('body', sa.Text(), nullable=False),
        sa.Column('owner_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('status', sa.Text(), server_default='active', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.Column('last_verified_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('embedding', pgvector_Vector(1536), nullable=True),
        sa.Column('import_source', sa.Text(), nullable=True),
        sa.CheckConstraint("type IN ('project', 'reference')", name='memories_type_check'),
        sa.CheckConstraint("status IN ('active', 'archived', 'disputed')", name='memories_status_check'),
        sa.UniqueConstraint('owner_id', 'name', name='memories_owner_name_uk'),
    )
    op.create_index('ix_memories_owner_id', 'memories', ['owner_id'])
    op.create_index('ix_memories_type', 'memories', ['type'])
    op.create_index('ix_memories_updated_at', 'memories', ['updated_at'])
    op.create_index('ix_memories_status', 'memories', ['status'])

    # Create tags table
    op.create_table('tags',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), primary_key=True),
        sa.Column('name', sa.Text(), nullable=False, unique=True),
    )

    # Create memory_tags association table
    op.create_table('memory_tags',
        sa.Column('memory_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('memories.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('tag_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('tags.id', ondelete='CASCADE'), primary_key=True),
    )

    # Create confirmations table
    op.create_table('confirmations',
        sa.Column('memory_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('memories.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('confirmed_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('note', sa.Text(), nullable=True),
    )

    # Create memory_history table
    op.create_table('memory_history',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), primary_key=True),
        sa.Column('memory_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('memories.id', ondelete='CASCADE'), nullable=False),
        sa.Column('body', sa.Text(), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('edited_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('edited_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # Create access_log table
    op.create_table('access_log',
        sa.Column('id', sa.BigInteger(), sa.Identity(start=1, increment=1), primary_key=True),
        sa.Column('memory_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('memories.id', ondelete='CASCADE'), nullable=False),
        sa.Column('read_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('accessed_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_access_log_memory_id', 'access_log', ['memory_id'])
    op.create_index('ix_access_log_read_by', 'access_log', ['read_by'])
    op.create_index('ix_access_log_accessed_at', 'access_log', ['accessed_at'])


def downgrade() -> None:
    op.drop_table('access_log')
    op.drop_table('memory_history')
    op.drop_table('confirmations')
    op.drop_table('memory_tags')
    op.drop_table('tags')
    op.drop_table('memories')
    op.drop_table('users')
