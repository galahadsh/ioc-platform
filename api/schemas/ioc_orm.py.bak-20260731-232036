from datetime import datetime

from pydantic import BaseModel, ConfigDict


class IOCResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

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


class IOCDetail(BaseModel):
    id: int

    tipo: str
    valor: str

    campaign: str | None = None
    malware_family: str | None = None

    fuente: str | None = None

    vt_estado: str | None = None
    vt_score: int | None = None

    vt_malicious: int | None = None
    vt_suspicious: int | None = None
    vt_harmless: int | None = None
    vt_undetected: int | None = None

    ultima_consulta: datetime | None = None

    model_config = ConfigDict(
        from_attributes=True
    )