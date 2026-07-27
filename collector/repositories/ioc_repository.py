from typing import Any

from psycopg2.extensions import connection


def get_pending_iocs(
    conn: connection,
    limit: int,
    max_retries: int,
) -> list[tuple]:
    """
    Obtiene IOC pendientes que todavía no alcanzan
    el máximo de reintentos.
    """

    with conn.cursor() as cursor:
        cursor.execute(
            """
            SELECT
                id,
                analysis_id,
                tipo,
                valor,
                COALESCE(vt_retry_count, 0)
            FROM iocs
            WHERE vt_estado = 'pendiente'
              AND COALESCE(vt_retry_count, 0) < %s
            ORDER BY id
            LIMIT %s
            FOR UPDATE SKIP LOCKED
            """,
            (
                max_retries,
                limit,
            ),
        )

        return cursor.fetchall()


def mark_analyzed(
    conn: connection,
    ioc_id: int,
    stats: dict[str, Any],
) -> None:
    """
    Marca un IOC como analizado y guarda
    las estadísticas de VirusTotal.
    """

    malicious = stats.get("malicious", 0)
    suspicious = stats.get("suspicious", 0)
    harmless = stats.get("harmless", 0)
    undetected = stats.get("undetected", 0)

    with conn.cursor() as cursor:
        cursor.execute(
            """
            UPDATE iocs
            SET
                vt_malicious = %s,
                vt_suspicious = %s,
                vt_harmless = %s,
                vt_undetected = %s,
                vt_score = %s,
                proveedor_reputacion = 'VirusTotal',
                vt_estado = 'analizado',
                vt_http_code = 200,
                vt_error = NULL,
                ultima_consulta = CURRENT_TIMESTAMP
            WHERE id = %s
            """,
            (
                malicious,
                suspicious,
                harmless,
                undetected,
                malicious,
                ioc_id,
            ),
        )


def mark_error(
    conn: connection,
    ioc_id: int,
    status_code: int | None,
    error: str,
) -> None:
    """
    Marca un IOC con error definitivo.
    """

    with conn.cursor() as cursor:
        cursor.execute(
            """
            UPDATE iocs
            SET
                vt_estado = 'error',
                vt_http_code = %s,
                vt_error = %s,
                ultima_consulta = CURRENT_TIMESTAMP
            WHERE id = %s
            """,
            (
                status_code,
                error[:1000],
                ioc_id,
            ),
        )


def increment_retry(
    conn: connection,
    ioc_id: int,
    status_code: int | None,
    error: str,
) -> None:
    """
    Incrementa el contador de reintentos para
    errores temporales.
    """

    with conn.cursor() as cursor:
        cursor.execute(
            """
            UPDATE iocs
            SET
                vt_retry_count =
                    COALESCE(vt_retry_count, 0) + 1,
                vt_http_code = %s,
                vt_error = %s,
                ultima_consulta = CURRENT_TIMESTAMP
            WHERE id = %s
            """,
            (
                status_code,
                error[:1000],
                ioc_id,
            ),
        )