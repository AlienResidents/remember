---
type: Source Code
description: "add unique constraint on users(provider, provider_id)"
resource: server/alembic/versions/002_unique_provider_id.py
timestamp: 2026-07-10T16:49:19Z
---

# 002 unique provider id

Source path: `server/alembic/versions/002_unique_provider_id.py`

## Content

```python
"""add unique constraint on users(provider, provider_id)

Revision ID: 002
Revises: 001
Create Date: 2026-07-10 00:00:00.000000

L3: Prevents duplicate User rows from concurrent get-or-create race conditions.
Without this, two simultaneous first-login requests for the same Keycloak user
could create two User rows, splitting their memories across two identities.
"""
from alembic import op

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add unique constraint on (provider, provider_id)
    # This prevents duplicate users from concurrent get-or-create races.
    op.create_unique_constraint(
        'users_provider_provider_id_uk',
        'users',
        ['provider', 'provider_id'],
    )


def downgrade() -> None:
    op.drop_constraint('users_provider_provider_id_uk', 'users', type_='unique')```

*…truncated — full source at `server/alembic/versions/002_unique_provider_id.py`*
