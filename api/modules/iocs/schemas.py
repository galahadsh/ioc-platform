from datetime import datetime

from pydantic import BaseModel, ConfigDict


class IOCResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: int
    analysis_id: int | None = None
    tipo: str
    valor: str
    fuente: str | None = None
    proveedor_reputacion: str | None = None

    vt_estado: str | None = None
    vt_score: int | None = None
    vt_malicious: int | None = None
    vt_suspicious: int | None = None
    vt_harmless: int | None = None
    vt_undetected: int | None = None

    fecha_creacion: datetime | None = None
    ultima_consulta: datetime | None = None

    vt_http_code: int | None = None
    vt_error: str | None = None
    vt_retry_count: int | None = None

    campaign: str | None = None
    malware_family: str | None = None


class IOCDetail(IOCResponse):
    pass


class PaginationMetadata(BaseModel):
    page: int
    page_size: int
    total: int
    total_pages: int
    has_previous: bool
    has_next: bool


class IOCListResponse(BaseModel):
    items: list[IOCResponse]
    pagination: PaginationMetadata
