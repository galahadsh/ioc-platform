from psycopg2.extensions import connection


def claim_pending_job(
    conn: connection,
    provider: str = "virustotal",
) -> dict | None:
    """
    Toma el siguiente job pendiente y lo marca
    como running de forma atómica.
    """

    with conn.cursor() as cursor:
        cursor.execute(
            """
            SELECT
                id,
                provider,
                total_items
            FROM enrichment_jobs
            WHERE provider = %s
              AND status = 'pending'
            ORDER BY created_at
            LIMIT 1
            FOR UPDATE SKIP LOCKED
            """,
            (provider,),
        )

        row = cursor.fetchone()

        if row is None:
            return None

        job_id, job_provider, total_items = row

        cursor.execute(
            """
            UPDATE enrichment_jobs
            SET
                status = 'running',
                started_at = CURRENT_TIMESTAMP,
                completed_at = NULL,
                error = NULL
            WHERE id = %s
            """,
            (job_id,),
        )

        return {
            "id": job_id,
            "provider": job_provider,
            "total_items": total_items,
        }


def update_job_progress(
    conn: connection,
    job_id: int,
) -> None:
    """
    Actualiza el progreso usando el estado actual
    de los IOC de la base.
    """

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
            analyzed_at_start = 0
            errors_at_start = 0
        else:
            analyzed_at_start, errors_at_start = baseline

        successful = max(
            analyzed - analyzed_at_start,
            0,
        )

        failed = max(
            errors - errors_at_start,
            0,
        )

        processed = successful + failed

        cursor.execute(
            """
            UPDATE enrichment_jobs
            SET
                processed_items = %s,
                successful_items = %s,
                failed_items = %s
            WHERE id = %s
            """,
            (
                processed,
                successful,
                failed,
                job_id,
            ),
        )


def create_job_baseline(
    conn: connection,
    job_id: int,
) -> None:
    """
    Registra los conteos existentes antes de iniciar
    el trabajo para calcular solo el progreso nuevo.
    """

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
            VALUES (%s, %s, %s)
            ON CONFLICT (job_id) DO NOTHING
            """,
            (
                job_id,
                analyzed,
                errors,
            ),
        )


def complete_job(
    conn: connection,
    job_id: int,
) -> None:
    update_job_progress(
        conn=conn,
        job_id=job_id,
    )

    with conn.cursor() as cursor:
        cursor.execute(
            """
            UPDATE enrichment_jobs
            SET
                status = 'completed',
                completed_at = CURRENT_TIMESTAMP
            WHERE id = %s
            """,
            (job_id,),
        )


def fail_job(
    conn: connection,
    job_id: int,
    error: str,
) -> None:
    with conn.cursor() as cursor:
        cursor.execute(
            """
            UPDATE enrichment_jobs
            SET
                status = 'failed',
                completed_at = CURRENT_TIMESTAMP,
                error = %s
            WHERE id = %s
            """,
            (
                error[:2000],
                job_id,
            ),
        )
