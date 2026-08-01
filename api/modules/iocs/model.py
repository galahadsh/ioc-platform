from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class IOC(Base):
    __tablename__ = "iocs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    analysis_id: Mapped[int | None] = mapped_column(Integer, nullable=True)

    tipo: Mapped[str] = mapped_column(String, nullable=False)
    valor: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    fuente: Mapped[str | None] = mapped_column(String, nullable=True)
    proveedor_reputacion: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )

    vt_estado: Mapped[str | None] = mapped_column(String, nullable=True)
    vt_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    vt_malicious: Mapped[int | None] = mapped_column(Integer, nullable=True)
    vt_suspicious: Mapped[int | None] = mapped_column(Integer, nullable=True)
    vt_harmless: Mapped[int | None] = mapped_column(Integer, nullable=True)
    vt_undetected: Mapped[int | None] = mapped_column(Integer, nullable=True)

    fecha_creacion: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )
    ultima_consulta: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    vt_http_code: Mapped[int | None] = mapped_column(Integer, nullable=True)
    vt_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    vt_retry_count: Mapped[int | None] = mapped_column(Integer, nullable=True)

    campaign: Mapped[str | None] = mapped_column(String, nullable=True)
    malware_family: Mapped[str | None] = mapped_column(String, nullable=True)

    def __repr__(self) -> str:
        return (
            f"IOC(id={self.id!r}, tipo={self.tipo!r}, "
            f"valor={self.valor!r})"
        )
