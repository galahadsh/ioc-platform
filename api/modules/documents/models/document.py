from __future__ import annotations

import uuid as uuid_lib
from datetime import datetime

from sqlalchemy import (
    BigInteger,
    DateTime,
    ForeignKey,
    SmallInteger,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base
from modules.documents.models.document_status import (
    DocumentStatus,
)


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
    )

    uuid: Mapped[uuid_lib.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        unique=True,
        default=uuid_lib.uuid4,
    )

    original_name: Mapped[str] = mapped_column(
        String(512),
        nullable=False,
    )

    stored_name: Mapped[str] = mapped_column(
        String(512),
        nullable=False,
    )

    bucket: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    object_name: Mapped[str] = mapped_column(
        String(1024),
        nullable=False,
    )

    content_type: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    extension: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    size_bytes: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
    )

    sha256: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )

    md5: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
    )

    source: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    tlp: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
    )

    classification: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    status_id: Mapped[int] = mapped_column(
        SmallInteger,
        ForeignKey("document_status.id"),
        nullable=False,
    )

    uploaded_by: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    processed_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    status: Mapped[DocumentStatus] = relationship(
        back_populates="documents",
    )

    def __repr__(self) -> str:
        return (
            "<Document("
            f"id={self.id}, "
            f"uuid='{self.uuid}', "
            f"name='{self.original_name}'"
            ")>"
        )
