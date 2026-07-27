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