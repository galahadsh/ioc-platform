from uuid import UUID as PyUUID
from datetime import datetime
from typing import Any

from sqlalchemy import (
    BigInteger,
    DateTime,
    ForeignKey,
    String,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base

# Registra la tabla users en Base.metadata.
# Necesario para resolver ForeignKey("users.id").
from modules.auth.models import User  # noqa: F401


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
    )

    event_uuid: Mapped[PyUUID] = mapped_column(
        UUID(as_uuid=True),
        unique=True,
        nullable=False,
    )

    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    user_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey(
            "users.id",
            ondelete="SET NULL",
        ),
    )

    username: Mapped[str | None] = mapped_column(
        String(100),
    )

    action: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    resource_type: Mapped[str | None] = mapped_column(
        String(100),
    )

    resource_id: Mapped[str | None] = mapped_column(
        String(255),
    )

    result: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    ip_address: Mapped[str | None] = mapped_column(
        String(64),
    )

    user_agent: Mapped[str | None] = mapped_column(
        String(512),
    )

    request_id: Mapped[PyUUID | None] = mapped_column(
        UUID(as_uuid=True),
    )

    details: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
