from datetime import date, timedelta
from typing import Any

from sqlalchemy import text
from sqlalchemy.engine import Engine


ALLOWED_ORDER_FIELDS = {
    "id": "id",
    "tipo": "tipo",
    "valor": "valor",
    "campaign": "campaign",
    "malware_family": "malware_family",
    "estado": "vt_estado",
    "score": "vt_score",
    "fecha_creacion": "fecha_creacion",
    "ultima_consulta": "ultima_consulta",
}


def _build_filters(
    search: str | None = None,
    tipo: str | None = None,
    estado: str | None = None,
    fuente: str | None = None,
    campaign: str | None = None,
    malware_family: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
) -> tuple[str, dict[str, Any]]:
    conditions = []
    params: dict[str, Any] = {}

    if search:
        conditions.append(
            """
            (
                valor ILIKE :search
                OR campaign ILIKE :search
                OR malware_family ILIKE :search
            )
            """
        )
        params["search"] = f"%{search.strip()}%"

    if tipo:
        conditions.append(
            "LOWER(tipo) = LOWER(:tipo)"
        )
        params["tipo"] = tipo.strip()

    if estado:
        conditions.append(
            "LOWER(vt_estado) = LOWER(:estado)"
        )
        params["estado"] = estado.strip()

    if fuente:
        conditions.append(
            "fuente ILIKE :fuente"
        )
        params["fuente"] = f"%{fuente.strip()}%"

    if campaign:
        conditions.append(
            "campaign ILIKE :campaign"
        )
        params["campaign"] = (
            f"%{campaign.strip()}%"
        )

    if malware_family:
        conditions.append(
            "malware_family ILIKE :malware_family"
        )
        params["malware_family"] = (
            f"%{malware_family.strip()}%"
        )

    if date_from:
        conditions.append(
            "fecha_creacion >= :date_from"
        )
        params["date_from"] = date_from

    if date_to:
        conditions.append(
            "fecha_creacion < :date_to_exclusive"
        )
        params["date_to_exclusive"] = (
            date_to + timedelta(days=1)
        )

    where_clause = ""

    if conditions:
        where_clause = (
            "WHERE " + " AND ".join(conditions)
        )

    return where_clause, params


def get_iocs(
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
) -> tuple[list[dict[str, Any]], int]:
    where_clause, params = _build_filters(
        search=search,
        tipo=tipo,
        estado=estado,
        fuente=fuente,
        campaign=campaign,
        malware_family=malware_family,
        date_from=date_from,
        date_to=date_to,
    )

    order_column = ALLOWED_ORDER_FIELDS.get(
        order_by,
        "fecha_creacion",
    )

    direction = (
        "ASC"
        if order_direction.lower() == "asc"
        else "DESC"
    )

    offset = (page - 1) * page_size

    count_query = text(
        f"""
        SELECT COUNT(*) AS total
        FROM iocs
        {where_clause}
        """
    )

    data_query = text(
        f"""
        SELECT
            id,
            analysis_id,
            tipo,
            valor,
            campaign,
            malware_family,
            fuente,
            proveedor_reputacion,
            vt_estado,
            vt_score,
            vt_malicious,
            vt_suspicious,
            vt_harmless,
            vt_undetected,
            fecha_creacion,
            ultima_consulta,
            vt_http_code,
            vt_error,
            vt_retry_count
        FROM iocs
        {where_clause}
        ORDER BY {order_column} {direction}, id DESC
        LIMIT :page_size
        OFFSET :offset
        """
    )

    query_params = {
        **params,
        "page_size": page_size,
        "offset": offset,
    }

    with engine.connect() as conn:
        total = conn.execute(
            count_query,
            params,
        ).scalar_one()

        rows = conn.execute(
            data_query,
            query_params,
        ).mappings().all()

    return [dict(row) for row in rows], total


def get_iocs_for_export(
    engine: Engine,
    search: str | None = None,
    tipo: str | None = None,
    estado: str | None = None,
    fuente: str | None = None,
    campaign: str | None = None,
    malware_family: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
) -> list[dict[str, Any]]:
    where_clause, params = _build_filters(
        search=search,
        tipo=tipo,
        estado=estado,
        fuente=fuente,
        campaign=campaign,
        malware_family=malware_family,
        date_from=date_from,
        date_to=date_to,
    )

    query = text(
        f"""
        SELECT
            id,
            analysis_id,
            tipo,
            valor,
            campaign,
            malware_family,
            fuente,
            proveedor_reputacion,
            vt_estado,
            vt_score,
            vt_malicious,
            vt_suspicious,
            vt_harmless,
            vt_undetected,
            fecha_creacion,
            ultima_consulta,
            vt_http_code,
            vt_error,
            vt_retry_count
        FROM iocs
        {where_clause}
        ORDER BY fecha_creacion DESC, id DESC
        """
    )

    with engine.connect() as conn:
        rows = conn.execute(
            query,
            params,
        ).mappings().all()

    return [dict(row) for row in rows]
