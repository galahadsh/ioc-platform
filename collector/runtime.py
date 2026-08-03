from typing import Any

from psycopg2.extensions import connection

from event_logger import add_event


ACTIVE_STATUSES = (
    "pending",
    "running",
    "paused",
)


def claim_next_job(
    conn: connection,
) -> dict[str, Any] | None:
    """
    Toma de forma exclusiva el siguiente trabajo pendiente.
    """

    with conn.cursor() as cursor:
        cursor.execute(
            """
            SELECT
                id,
                provider,
                total_items,
                COALESCE(max_attempts, 3),
                COALESCE(rate_limit_per_minute, 4)
            FROM enrichment_jobs
            WHERE provider = 'virustotal'
              AND status = 'pending'
            ORDER BY created_at
            LIMIT 1
            FOR UPDATE SKIP LOCKED
            """
        )

        row = cursor.fetchone()

        if row is None:
            return None

        job = {
            "id": row[0],
            "provider": row[1],
            "total_items": int(row[2] or 0),
            "max_attempts": int(row[3] or 3),
            "rate_limit_per_minute": int(
                row[4] or 4
            ),
        }

        cursor.execute(
            """
            UPDATE enrichment_jobs
            SET
                status = 'running',
                started_at = COALESCE(
                    started_at,
                    CURRENT_TIMESTAMP
                ),
                completed_at = NULL,
                error = NULL,
                pause_requested = FALSE,
                cancel_requested = FALSE,
                last_activity_at = CURRENT_TIMESTAMP
            WHERE id = %s
            """,
            (job["id"],),
        )

    add_event(
        conn=conn,
        job_id=job["id"],
        level="INFO",
        event_type="job_started",
        message=(
            "Trabajo iniciado. "
            f"Proveedor={job['provider']} "
            f"Total={job['total_items']} "
            f"Rate={job['rate_limit_per_minute']}/min."
        ),
    )

    return job


def get_control_state(
    conn: connection,
    job_id: int,
) -> dict[str, Any] | None:
    """
    Lee las solicitudes de pausa y cancelación.
    """

    with conn.cursor() as cursor:
        cursor.execute(
            """
            SELECT
                status,
                pause_requested,
                cancel_requested
            FROM enrichment_jobs
            WHERE id = %s
            """,
            (job_id,),
        )

        row = cursor.fetchone()

    if row is None:
        return None

    return {
        "status": row[0],
        "pause_requested": bool(row[1]),
        "cancel_requested": bool(row[2]),
    }


def set_paused(
    conn: connection,
    job_id: int,
) -> None:
    with conn.cursor() as cursor:
        cursor.execute(
            """
            UPDATE enrichment_jobs
            SET
                status = 'paused',
                last_activity_at = CURRENT_TIMESTAMP
            WHERE id = %s
            """,
            (job_id,),
        )

    add_event(
        conn=conn,
        job_id=job_id,
        level="WARN",
        event_type="job_paused",
        message=(
            "Trabajo pausado. El collector "
            "esperará una solicitud de reanudación."
        ),
    )


def set_running(
    conn: connection,
    job_id: int,
) -> None:
    with conn.cursor() as cursor:
        cursor.execute(
            """
            UPDATE enrichment_jobs
            SET
                status = 'running',
                pause_requested = FALSE,
                last_activity_at = CURRENT_TIMESTAMP
            WHERE id = %s
            """,
            (job_id,),
        )

    add_event(
        conn=conn,
        job_id=job_id,
        level="INFO",
        event_type="job_resumed",
        message="Trabajo reanudado.",
    )


def set_current_ioc(
    conn: connection,
    job_id: int,
    ioc_id: int,
    ioc_type: str,
    value: str,
    source: str | None,
    attempt: int,
) -> None:
    with conn.cursor() as cursor:
        cursor.execute(
            """
            UPDATE enrichment_jobs
            SET
                current_ioc_id = %s,
                current_ioc_type = %s,
                current_ioc_value = %s,
                current_ioc_source = %s,
                current_attempt = %s,
                last_activity_at = CURRENT_TIMESTAMP
            WHERE id = %s
            """,
            (
                ioc_id,
                ioc_type,
                value,
                source,
                attempt,
                job_id,
            ),
        )


def clear_current_ioc(
    conn: connection,
    job_id: int,
) -> None:
    with conn.cursor() as cursor:
        cursor.execute(
            """
            UPDATE enrichment_jobs
            SET
                current_ioc_id = NULL,
                current_ioc_type = NULL,
                current_ioc_value = NULL,
                current_ioc_source = NULL,
                current_attempt = 0,
                last_activity_at = CURRENT_TIMESTAMP
            WHERE id = %s
            """,
            (job_id,),
        )


def create_baseline(
    conn: connection,
    job_id: int,
) -> None:
    with conn.cursor() as cursor:
        cursor.execute(
            """
            SELECT
                COUNT(*) FILTER (
                    WHERE vt_estado = 'analizado'
                ),
                COUNT(*) FILTER (
                    WHERE vt_estado = 'error'
                )
            FROM iocs
            """
        )

        analyzed, errors = cursor.fetchone()

        cursor.execute(
            """
            INSERT INTO enrichment_job_baselines (
                job_id,
                analyzed_at_start,
                errors_at_start
            )
            VALUES (
                %s,
                %s,
                %s
            )
            ON CONFLICT (job_id) DO NOTHING
            """,
            (
                job_id,
                int(analyzed or 0),
                int(errors or 0),
            ),
        )


def update_progress(
    conn: connection,
    job_id: int,
) -> dict[str, int]:
    with conn.cursor() as cursor:
        cursor.execute(
            """
            SELECT
                analyzed_at_start,
                errors_at_start
            FROM enrichment_job_baselines
            WHERE job_id = %s
            """,
            (job_id,),
        )

        baseline = cursor.fetchone()

        if baseline is None:
            analyzed_start = 0
            errors_start = 0
        else:
            analyzed_start = int(
                baseline[0] or 0
            )
            errors_start = int(
                baseline[1] or 0
            )

        cursor.execute(
            """
            SELECT
                COUNT(*) FILTER (
                    WHERE vt_estado = 'analizado'
                ),
                COUNT(*) FILTER (
                    WHERE vt_estado = 'error'
                )
            FROM iocs
            """
        )

        analyzed, errors = cursor.fetchone()

        successful = max(
            int(analyzed or 0) - analyzed_start,
            0,
        )

        failed = max(
            int(errors or 0) - errors_start,
            0,
        )

        processed = successful + failed

        cursor.execute(
            """
            UPDATE enrichment_jobs
            SET
                processed_items = %s,
                successful_items = %s,
                failed_items = %s,
                last_activity_at = CURRENT_TIMESTAMP
            WHERE id = %s
            """,
            (
                processed,
                successful,
                failed,
                job_id,
            ),
        )

    return {
        "processed": processed,
        "successful": successful,
        "failed": failed,
    }


def complete_job(
    conn: connection,
    job_id: int,
) -> None:
    progress = update_progress(
        conn=conn,
        job_id=job_id,
    )

    clear_current_ioc(
        conn=conn,
        job_id=job_id,
    )

    with conn.cursor() as cursor:
        cursor.execute(
            """
            UPDATE enrichment_jobs
            SET
                status = 'completed',
                completed_at = CURRENT_TIMESTAMP,
                pause_requested = FALSE,
                cancel_requested = FALSE,
                last_activity_at = CURRENT_TIMESTAMP
            WHERE id = %s
            """,
            (job_id,),
        )

    add_event(
        conn=conn,
        job_id=job_id,
        level="INFO",
        event_type="job_completed",
        message=(
            "Trabajo completado. "
            f"Procesados={progress['processed']} "
            f"Exitosos={progress['successful']} "
            f"Fallidos={progress['failed']}."
        ),
    )


def cancel_job(
    conn: connection,
    job_id: int,
) -> None:
    progress = update_progress(
        conn=conn,
        job_id=job_id,
    )

    clear_current_ioc(
        conn=conn,
        job_id=job_id,
    )

    with conn.cursor() as cursor:
        cursor.execute(
            """
            UPDATE enrichment_jobs
            SET
                status = 'cancelled',
                completed_at = CURRENT_TIMESTAMP,
                pause_requested = FALSE,
                cancel_requested = TRUE,
                last_activity_at = CURRENT_TIMESTAMP
            WHERE id = %s
            """,
            (job_id,),
        )

    add_event(
        conn=conn,
        job_id=job_id,
        level="WARN",
        event_type="job_cancelled",
        message=(
            "Trabajo cancelado. "
            f"Procesados={progress['processed']}."
        ),
    )


def fail_job(
    conn: connection,
    job_id: int,
    error: str,
) -> None:
    clear_current_ioc(
        conn=conn,
        job_id=job_id,
    )

    with conn.cursor() as cursor:
        cursor.execute(
            """
            UPDATE enrichment_jobs
            SET
                status = 'failed',
                completed_at = CURRENT_TIMESTAMP,
                error = %s,
                last_activity_at = CURRENT_TIMESTAMP
            WHERE id = %s
            """,
            (
                error[:2000],
                job_id,
            ),
        )

    add_event(
        conn=conn,
        job_id=job_id,
        level="ERROR",
        event_type="job_failed",
        message=f"Trabajo fallido: {error}",
    )
