import logging
import time

from clients.virustotal import VirusTotalClient
from config import (
    COLLECTOR_BATCH_SIZE,
    COLLECTOR_INTERVAL,
    VT_MAX_RETRIES,
    validate_config,
)
from database import get_connection
from repositories.ioc_repository import (
    get_pending_iocs,
)
from repositories.job_repository import (
    claim_pending_job,
    complete_job,
    create_job_baseline,
    fail_job,
    update_job_progress,
)
from services.analysis_service import update_analysis
from services.enrichment_service import process_ioc


logging.basicConfig(
    level=logging.INFO,
    format=(
        "%(asctime)s %(levelname)s "
        "%(name)s %(message)s"
    ),
)

logger = logging.getLogger("ioc-collector")


def process_job(job: dict) -> None:
    job_id = job["id"]

    logger.info(
        "Iniciando job VT id=%s total=%s",
        job_id,
        job["total_items"],
    )

    conn = get_connection()

    try:
        create_job_baseline(
            conn=conn,
            job_id=job_id,
        )

        conn.commit()

        vt_client = VirusTotalClient()

        while True:
            pending_iocs = get_pending_iocs(
                conn=conn,
                limit=COLLECTOR_BATCH_SIZE,
                max_retries=VT_MAX_RETRIES,
            )

            if not pending_iocs:
                conn.rollback()
                break

            analysis_ids = set()

            for (
                ioc_id,
                analysis_id,
                ioc_type,
                value,
                retry_count,
            ) in pending_iocs:
                try:
                    process_ioc(
                        conn=conn,
                        client=vt_client,
                        ioc_id=ioc_id,
                        ioc_type=ioc_type,
                        value=value,
                        retry_count=retry_count,
                    )

                    if analysis_id is not None:
                        analysis_ids.add(
                            analysis_id
                        )

                    update_job_progress(
                        conn=conn,
                        job_id=job_id,
                    )

                    conn.commit()

                except Exception:
                    conn.rollback()

                    logger.exception(
                        "Error procesando IOC id=%s",
                        ioc_id,
                    )

            for analysis_id in analysis_ids:
                try:
                    update_analysis(
                        conn=conn,
                        analysis_id=analysis_id,
                    )

                    conn.commit()

                except Exception:
                    conn.rollback()

                    logger.exception(
                        "Error actualizando análisis id=%s",
                        analysis_id,
                    )

        complete_job(
            conn=conn,
            job_id=job_id,
        )

        conn.commit()

        logger.info(
            "Job VT id=%s completado",
            job_id,
        )

    except Exception as error:
        conn.rollback()

        logger.exception(
            "Job VT id=%s falló",
            job_id,
        )

        try:
            fail_job(
                conn=conn,
                job_id=job_id,
                error=str(error),
            )

            conn.commit()

        except Exception:
            conn.rollback()

            logger.exception(
                "No se pudo marcar el job como fallido"
            )

    finally:
        conn.close()


def get_next_job() -> dict | None:
    conn = get_connection()

    try:
        job = claim_pending_job(
            conn=conn,
            provider="virustotal",
        )

        if job is None:
            conn.rollback()
            return None

        conn.commit()

        return job

    finally:
        conn.close()


def main() -> None:
    validate_config()

    logger.info(
        "Collector iniciado en modo manual"
    )

    logger.info(
        "Batch=%s Interval=%ss",
        COLLECTOR_BATCH_SIZE,
        COLLECTOR_INTERVAL,
    )

    while True:
        try:
            job = get_next_job()

            if job is None:
                time.sleep(
                    COLLECTOR_INTERVAL
                )
                continue

            process_job(job)

        except KeyboardInterrupt:
            logger.info("Collector detenido")
            break

        except Exception:
            logger.exception(
                "Error general del collector"
            )

            time.sleep(
                COLLECTOR_INTERVAL
            )


if __name__ == "__main__":
    main()
