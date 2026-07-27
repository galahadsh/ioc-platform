from sqlalchemy import text

from database import engine


def get_stats() -> dict:
    query = """
    SELECT
        COUNT(*) AS total,

        COUNT(*) FILTER (
            WHERE vt_estado = 'analizado'
              AND COALESCE(vt_malicious, 0) > 0
        ) AS maliciosos,

        COUNT(*) FILTER (
            WHERE vt_estado = 'analizado'
              AND COALESCE(vt_malicious, 0) = 0
              AND COALESCE(vt_suspicious, 0) > 0
        ) AS sospechosos,

        COUNT(*) FILTER (
            WHERE vt_estado = 'analizado'
              AND COALESCE(vt_malicious, 0) = 0
              AND COALESCE(vt_suspicious, 0) = 0
        ) AS limpios,

        COUNT(*) FILTER (
            WHERE COALESCE(vt_estado, 'pendiente') = 'pendiente'
        ) AS pendientes,

        COUNT(*) FILTER (
            WHERE vt_estado = 'error'
        ) AS errores

    FROM iocs;
    """

    with engine.connect() as conn:
        row = conn.execute(text(query)).mappings().one()

    return dict(row)


def get_iocs_by_type() -> list[dict]:
    query = """
    SELECT
        COALESCE(NULLIF(TRIM(tipo), ''), 'Sin tipo') AS label,
        COUNT(*) AS total
    FROM iocs
    GROUP BY COALESCE(NULLIF(TRIM(tipo), ''), 'Sin tipo')
    ORDER BY total DESC;
    """

    with engine.connect() as conn:
        rows = conn.execute(text(query)).mappings().all()

    return [dict(row) for row in rows]


def get_iocs_by_source(limit: int = 10) -> list[dict]:
    query = """
    SELECT
        COALESCE(NULLIF(TRIM(fuente), ''), 'Sin fuente') AS label,
        COUNT(*) AS total
    FROM iocs
    GROUP BY COALESCE(NULLIF(TRIM(fuente), ''), 'Sin fuente')
    ORDER BY total DESC
    LIMIT :limit;
    """

    with engine.connect() as conn:
        rows = conn.execute(
            text(query),
            {"limit": limit},
        ).mappings().all()

    return [dict(row) for row in rows]


def get_iocs_by_campaign(limit: int = 10) -> list[dict]:
    query = """
    SELECT
        COALESCE(
            NULLIF(TRIM(campaign), ''),
            'Sin campaña'
        ) AS label,
        COUNT(*) AS total
    FROM iocs
    GROUP BY COALESCE(
        NULLIF(TRIM(campaign), ''),
        'Sin campaña'
    )
    ORDER BY total DESC
    LIMIT :limit;
    """

    with engine.connect() as conn:
        rows = conn.execute(
            text(query),
            {"limit": limit},
        ).mappings().all()

    return [dict(row) for row in rows]


def get_iocs_by_malware(limit: int = 10) -> list[dict]:
    query = """
    SELECT
        COALESCE(
            NULLIF(TRIM(malware_family), ''),
            'No identificado'
        ) AS label,
        COUNT(*) AS total
    FROM iocs
    GROUP BY COALESCE(
        NULLIF(TRIM(malware_family), ''),
        'No identificado'
    )
    ORDER BY total DESC
    LIMIT :limit;
    """

    with engine.connect() as conn:
        rows = conn.execute(
            text(query),
            {"limit": limit},
        ).mappings().all()

    return [dict(row) for row in rows]


def get_iocs_by_month(limit: int = 12) -> list[dict]:
    query = """
    SELECT
        TO_CHAR(
            DATE_TRUNC('month', ultima_consulta),
            'YYYY-MM'
        ) AS label,
        COUNT(*) AS total
    FROM iocs
    WHERE ultima_consulta IS NOT NULL
    GROUP BY DATE_TRUNC('month', ultima_consulta)
    ORDER BY DATE_TRUNC('month', ultima_consulta) DESC
    LIMIT :limit;
    """

    with engine.connect() as conn:
        rows = conn.execute(
            text(query),
            {"limit": limit},
        ).mappings().all()

    result = [dict(row) for row in rows]

    return list(reversed(result))


def get_statistics() -> dict:
    return {
        "summary": get_stats(),
        "by_type": get_iocs_by_type(),
        "by_source": get_iocs_by_source(),
        "by_campaign": get_iocs_by_campaign(),
        "by_malware": get_iocs_by_malware(),
        "by_month": get_iocs_by_month(),
    }