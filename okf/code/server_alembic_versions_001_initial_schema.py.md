---
type: Source Code
description: "initial schema"
resource: server/alembic/versions/001_initial_schema.py
timestamp: 2026-07-09T01:43:39Z
---

# 001 initial schema

Source path: `server/alembic/versions/001_initial_schema.py`

## Content

```python
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
```

*…truncated — full source at `server/alembic/versions/001_initial_schema.py`*
