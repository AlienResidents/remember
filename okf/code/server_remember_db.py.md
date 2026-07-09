---
type: Source Code
description: "Database connection and session management."
resource: server/remember/db.py
timestamp: 2026-07-09T01:43:39Z
---

# db

Source path: `server/remember/db.py`

## Content

```python
"""Database connection and session management."""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from remember.config import Settings

settings = Settings()

engine = create_async_engine(
    settings.database.async_url,
    echo=settings.database.echo,
    pool_size=settings.database.pool_size,
    max_overflow=settings.database.max_overflow,
)

async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """Base class for SQLAlchemy models."""

    pass


async def get_db() -> AsyncSession:
    """Get a database session."""
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """Initialize the database (create tables)."""
```

*…truncated — full source at `server/remember/db.py`*
