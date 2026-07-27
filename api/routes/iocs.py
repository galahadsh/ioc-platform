from datetime import date
from io import BytesIO

from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse
from sqlalchemy import text

from database import engine
from services.ioc_service import (
    export_iocs_csv,
    list_iocs,
)


router = APIRouter(
    prefix="/api/iocs",
    tags=["IOCs"],
)


@router.get("")
def get_iocs(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=25, ge=10, le=100),
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
):
    return list_iocs(
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


@router.get("/export")
def export_iocs(
    search: str | None = None,
    tipo: str | None = None,
    estado: str | None = None,
    fuente: str | None = None,
    campaign: str | None = None,
    malware_family: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
):
    csv_content = export_iocs_csv(
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

    filename_from = (
        date_from.isoformat()
        if date_from
        else "inicio"
    )

    filename_to = (
        date_to.isoformat()
        if date_to
        else "actual"
    )

    filename = (
        f"iocs_{filename_from}_{filename_to}.csv"
    )

    csv_bytes = csv_content.encode("utf-8-sig")

    return StreamingResponse(
        BytesIO(csv_bytes),
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": (
                f'attachment; filename="{filename}"'
            )
        },
    )


@router.get("/malicious")
def malicious_iocs():
    query = """
    SELECT
        id,
        tipo,
        valor,
        campaign,
        malware_family,
        vt_malicious,
        vt_suspicious,
        vt_score,
        proveedor_reputacion,
        vt_estado,
        fuente,
        fecha_creacion
    FROM iocs
    WHERE COALESCE(vt_malicious, 0) > 0
    ORDER BY vt_malicious DESC, id DESC
    LIMIT 100;
    """

    with engine.connect() as conn:
        rows = conn.execute(
            text(query)
        ).mappings().all()

    return [
        {
            "id": row["id"],
            "tipo": row["tipo"],
            "valor": row["valor"],
            "campaign": row["campaign"],
            "malware_family": row[
                "malware_family"
            ],
            "malicious": row["vt_malicious"],
            "suspicious": row["vt_suspicious"],
            "vt_score": row["vt_score"],
            "proveedor": row[
                "proveedor_reputacion"
            ],
            "estado": row["vt_estado"],
            "fuente": row["fuente"],
            "fecha_creacion": (
                row["fecha_creacion"].isoformat()
                if row["fecha_creacion"]
                else None
            ),
        }
        for row in rows
    ]
