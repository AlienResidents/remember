"""SQLAlchemy models for REMEMBER."""

import uuid
from datetime import datetime, timezone

from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from remember.db import Base


class User(Base):
    """Team member."""

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    provider: Mapped[str] = mapped_column(Text, nullable=False)
    provider_id: Mapped[str] = mapped_column(Text, nullable=False, index=True)
    display_name: Mapped[str] = mapped_column(Text, nullable=False)
    email: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    last_seen_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    memories = relationship("Memory", back_populates="owner", cascade="all, delete-orphan")

    # L3: Unique constraint on (provider, provider_id) — prevents duplicate
    # users from concurrent get-or-create race conditions. Without this, two
    # simultaneous first-login requests for the same Keycloak user could
    # create two User rows, splitting their memories across two identities.
    __table_args__ = (
        UniqueConstraint("provider", "provider_id", name="users_provider_provider_id_uk"),
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, provider={self.provider}, provider_id={self.provider_id})>"


class Memory(Base):
    """A team memory."""

    __tablename__ = "memories"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    name: Mapped[str] = mapped_column(Text, nullable=False)
    type: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        server_default="project",
    )
    description: Mapped[str] = mapped_column(Text, nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    owner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    status: Mapped[str] = mapped_column(
        Text, nullable=False, server_default="active"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )
    last_verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    embedding: Mapped[Vector | None] = mapped_column(Vector(1536), nullable=True)
    import_source: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    owner = relationship("User", back_populates="memories")
    tags = relationship("Tag", secondary="memory_tags", back_populates="memories")
    confirmations = relationship("Confirmation", back_populates="memory", cascade="all, delete-orphan")
    history = relationship("MemoryHistory", back_populates="memory", cascade="all, delete-orphan")

    # Constraints
    __table_args__ = (
        CheckConstraint("type IN ('project', 'reference')", name="memories_type_check"),
        CheckConstraint(
            "status IN ('active', 'archived', 'disputed')", name="memories_status_check"
        ),
        UniqueConstraint("owner_id", "name", name="memories_owner_name_uk"),
        Index("ix_memories_owner_id", "owner_id"),
        Index("ix_memories_type", "type"),
        Index("ix_memories_updated_at", "updated_at"),
        Index("ix_memories_status", "status"),
    )

    def __repr__(self) -> str:
        return f"<Memory(id={self.id}, name={self.name}, type={self.type})>"


class Tag(Base):
    """A tag for categorizing memories."""

    __tablename__ = "tags"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    name: Mapped[str] = mapped_column(Text, nullable=False, unique=True)

    # Relationships
    memories = relationship("Memory", secondary="memory_tags", back_populates="tags")

    def __repr__(self) -> str:
        return f"<Tag(id={self.id}, name={self.name})>"


class MemoryTag(Base):
    """Association table between memories and tags."""

    __tablename__ = "memory_tags"

    memory_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("memories.id", ondelete="CASCADE"), primary_key=True
    )
    tag_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True
    )


class Confirmation(Base):
    """A confirmation or refutation of a memory."""

    __tablename__ = "confirmations"

    memory_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("memories.id", ondelete="CASCADE"), primary_key=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    confirmed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    note: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    memory = relationship("Memory", back_populates="confirmations")
    user = relationship("User")

    def __repr__(self) -> str:
        return f"<Confirmation(memory_id={self.memory_id}, user_id={self.user_id})>"


class MemoryHistory(Base):
    """History of memory edits (append-only)."""

    __tablename__ = "memory_history"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    memory_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("memories.id", ondelete="CASCADE"), nullable=False
    )
    body: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    edited_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    edited_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    # Relationships
    memory = relationship("Memory", back_populates="history")
    editor = relationship("User")

    def __repr__(self) -> str:
        return f"<MemoryHistory(id={self.id}, memory_id={self.memory_id})>"


class AccessLog(Base):
    """Log of memory reads (for analytics)."""

    __tablename__ = "access_log"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    memory_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("memories.id", ondelete="CASCADE"), nullable=False
    )
    read_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    accessed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    __table_args__ = (
        Index("ix_access_log_memory_id", "memory_id"),
        Index("ix_access_log_read_by", "read_by"),
        Index("ix_access_log_accessed_at", "accessed_at"),
    )

    def __repr__(self) -> str:
        return f"<AccessLog(id={self.id}, memory_id={self.memory_id})>"
