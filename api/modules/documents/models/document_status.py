from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import SmallInteger, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base

if TYPE_CHECKING:
    from modules.documents.models.document import Document


class DocumentStatus(Base):
    __tablename__ = "document_status"

    id: Mapped[int] = mapped_column(
        SmallInteger,
        primary_key=True,
    )

    code: Mapped[str] = mapped_column(
        String(30),
        unique=True,
        nullable=False,
    )

    name: Mapped[str] = mapped_column(
        String(60),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    documents: Mapped[list["Document"]] = relationship(
        back_populates="status",
    )

    def __repr__(self) -> str:
        return (
            "<DocumentStatus("
            f"id={self.id}, "
            f"code='{self.code}'"
            ")>"
        )
