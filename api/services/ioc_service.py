import csv
import io
import math
from datetime import date
from typing import Any

from sqlalchemy.engine import Engine

from repositories.ioc_repository import (
    get_iocs,
    get_iocs_for_export,
)


def _serialize_datetime(value: Any) -> Any:
    if value is None:
        return None

    if hasattr(value, "isoformat"):
        return value.isoformat()

    return value


def list_iocs(
    engine: Engine,
    page: int,
    page_size: int,
    search: str | None = None,
    tipo: str | None = None,
    estado: str | None = None,
    fuente: str | None = None,
    campaign: str | None = None,
    malware_family: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    order_by: str = "fecha_creacion",
    order_direction: str = "desc",
) -> dict[str, Any]:
    rows, total = get_iocs(
        engine=engine,
        page=page,
        page_size=page_size,
        search=search,
        tipo=tipo,
        estado=estado,
        fuente=fuente,
        campaign=campaign,
        malware_family=malware_family,
        date_from=date_from,
        date_to=date_to,
        order_by=order_by,
        order_direction=order_direction,
    )

    items = []

    for row in rows:
        items.append(
            {
                key: _serialize_datetime(value)
                for key, value in row.items()
            }
        )

    total_pages = (
        math.ceil(total / page_size)
        if total > 0
        else 0
    )

    return {
        "items": items,
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": total_pages,
            "has_previous": page > 1,
            "has_next": page < total_pages,
        },
    }


def export_iocs_csv(
    engine: Engine,
    search: str | None = None,
    tipo: str | None = None,
    estado: str | None = None,
    fuente: str | None = None,
    campaign: str | None = None,
    malware_family: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
) -> str:
    rows = get_iocs_for_export(
        engine=engine,
        search=search,
        tipo=tipo,
        estado=estado,
        fuente=fuente,
        campaign=campaign,
        malware_family=malware_family,
        date_from=date_from,
        date_to=date_to,
    )

    output = io.StringIO()

    fieldnames = [
        "id",
        "analysis_id",
        "tipo",
        "valor",
        "campaign",
        "malware_family",
        "fuente",
        "proveedor_reputacion",
        "vt_estado",
        "vt_score",
        "vt_malicious",
        "vt_suspicious",
        "vt_harmless",
        "vt_undetected",
        "fecha_creacion",
        "ultima_consulta",
        "vt_http_code",
        "vt_error",
        "vt_retry_count",
    ]

    writer = csv.DictWriter(
        output,
        fieldnames=fieldnames,
    )

    writer.writeheader()

    for row in rows:
        writer.writerow(
            {
                key: _serialize_datetime(row.get(key))
                for key in fieldnames
            }
        )

    return output.getvalue()
