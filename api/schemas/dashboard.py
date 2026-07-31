from datetime import datetime

from pydantic import BaseModel


class DashboardSummary(BaseModel):
    total: int
    analyzed: int
    malicious: int
    suspicious: int
    clean: int
    pending: int
    errors: int
    analyzed_percentage: float
    malicious_percentage: float


class DashboardAggregationItem(BaseModel):
    label: str
    total: int


class DashboardRecentIOC(BaseModel):
    id: int
    tipo: str
    valor: str
    vt_estado: str | None = None
    vt_score: int | None = None
    vt_malicious: int | None = None
    campaign: str | None = None
    malware_family: str | None = None
    fuente: str | None = None
    fecha_creacion: datetime | None = None
    ultima_consulta: datetime | None = None


class DashboardResponse(BaseModel):
    summary: DashboardSummary
    types: list[DashboardAggregationItem]
    sources: list[DashboardAggregationItem]
    campaigns: list[DashboardAggregationItem]
    malware: list[DashboardAggregationItem]
    monthly: list[DashboardAggregationItem]
    recent_iocs: list[DashboardRecentIOC]
    generated_at: datetime
