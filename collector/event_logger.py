import logging

from psycopg2.extensions import connection


logger = logging.getLogger("ioc-event-logger")


def add_event(
    conn: connection,
    job_id: int,
    message: str,
    level: str = "INFO",
    event_type: str = "general",
    ioc_id: int | None = None,
) -> None:
    """
    Guarda un evento visible en la consola web.
    """

    normalized_level = level.upper()

    with conn.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO enrichment_job_events (
                job_id,
                level,
                event_type,
                message,
                ioc_id,
                created_at
            )
            VALUES (
                %s,
                %s,
                %s,
                %s,
                %s,
                CURRENT_TIMESTAMP
            )
            """,
            (
                job_id,
                normalized_level,
                event_type,
                message[:4000],
                ioc_id,
            ),
        )

    log_method = {
        "DEBUG": logger.debug,
        "INFO": logger.info,
        "WARN": logger.warning,
        "WARNING": logger.warning,
        "ERROR": logger.error,
    }.get(
        normalized_level,
        logger.info,
    )

    log_method(
        "Job=%s IOC=%s %s",
        job_id,
        ioc_id,
        message,
    )
