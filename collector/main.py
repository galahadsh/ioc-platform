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
    add_job_event,
    cancel_job,
    claim_pending_job,
    complete_job,
    create_job_baseline,
    fail_job,
    get_job_control,
    mark_job_paused,
    mark_job_running,
    set_current_ioc,
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


def handle_job_control(
    conn,
    job_id: int,
) -> str:
    control = get_job_control(
        conn=conn,
        job_id=job_id,
    )

    if control is None:
        return "cancel"

    if control["cancel_requested"]:
        cancel_job(
            conn=conn,
            job_id=job_id,
        )

        conn.commit()
        return "cancel"

    if not control["pause_requested"]:
        return "continue"

    mark_job_paused(
        conn=conn,
        job_id=job_id,
    )

    conn.commit()

    while True:
        time.sleep(2)

        control = get_job_control(
            conn=conn,
            job_id=job_id,
        )

        if control is None:
            return "cancel"

        if control["cancel_requested"]:
            cancel_job(
                conn=conn,
                job_id=job_id,
            )

            conn.commit()
            return "cancel"

        if not control["pause_requested"]:
            mark_job_running(
                conn=conn,
                job_id=job_id,
            )

            conn.commit()
            return "continue"


def process_job(job: dict) -> None:
    job_id = job["id"]

    conn = get_connection()

    try:
        create_job_baseline(
            conn=conn,
            job_id=job_id,
        )

        add_job_event(
            conn=conn,
            job_id=job_id,
            level="INFO",
            event_type="queue_info",
            message=(
                "IOC pendientes en cola: "
                f"{job['total_items']}"
            ),
        )

        add_job_event(
            conn=conn,
            job_id=job_id,
            level="INFO",
            event_type="rate_limit",
            message=(
                "Límite configurado: "
                f"{job['rate_limit_per_minute']} "
                "consultas por minuto."
            ),
        )

        conn.commit()

        logger.info(
            "Iniciando job VT id=%s total=%s",
            job_id,
            job["total_items"],
        )

        vt_client = VirusTotalClient()

        while True:
            control_result = handle_job_control(
                conn=conn,
                job_id=job_id,
            )

            if control_result == "cancel":
                logger.info(
                    "Job VT id=%s cancelado",
                    job_id,
                )
                return

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
                source,
            ) in pending_iocs:
                control_result = handle_job_control(
                    conn=conn,
                    job_id=job_id,
                )

                if control_result == "cancel":
                    logger.info(
                        "Job VT id=%s cancelado",
                        job_id,
                    )
                    return

                progress = update_job_progress(
                    conn=conn,
                    job_id=job_id,
                )

                current_number = (
                    progress["processed"] + 1
                )

                attempt = retry_count + 1

                set_current_ioc(
                    conn=conn,
                    job_id=job_id,
                    ioc_id=ioc_id,
                    ioc_type=ioc_type,
                    value=value,
                    source=source,
                    attempt=attempt,
                )

                add_job_event(
                    conn=conn,
                    job_id=job_id,
                    level="INFO",
                    event_type="ioc_started",
                    ioc_id=ioc_id,
                    message=(
                        f"[{current_number}/"
                        f"{job['total_items']}] "
                        f"Consultando {value} "
                        f"({ioc_type})."
                    ),
                )

                conn.commit()

                try:
                    success = process_ioc(
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

                    progress = update_job_progress(
                        conn=conn,
                        job_id=job_id,
                    )

                    if success:
                        level = "INFO"
                        event_type = "ioc_analyzed"
                        message = (
                            f"IOC {value} analizado "
                            "correctamente."
                        )
                    else:
                        level = "WARN"
                        event_type = "ioc_pending_or_error"
                        message = (
                            f"IOC {value} no quedó "
                            "analizado en este intento."
                        )

                    add_job_event(
                        conn=conn,
                        job_id=job_id,
                        level=level,
                        event_type=event_type,
                        ioc_id=ioc_id,
                        message=message,
                    )

                    add_job_event(
                        conn=conn,
                        job_id=job_id,
                        level="DEBUG",
                        event_type="progress",
                        message=(
                            "Progreso actualizado: "
                            f"{progress['processed']} de "
                            f"{job['total_items']}."
                        ),
                    )

                    conn.commit()

                except Exception as error:
                    conn.rollback()

                    logger.exception(
                        "Error procesando IOC id=%s",
                        ioc_id,
                    )

                    add_job_event(
                        conn=conn,
                        job_id=job_id,
                        level="ERROR",
                        event_type="ioc_exception",
                        ioc_id=ioc_id,
                        message=(
                            f"Error procesando IOC "
                            f"{value}: {error}"
                        ),
                    )

                    conn.commit()

            for analysis_id in analysis_ids:
                try:
                    update_analysis(
                        conn=conn,
                        analysis_id=analysis_id,
                    )

                    conn.commit()

                except Exception as error:
                    conn.rollback()

                    logger.exception(
                        "Error actualizando análisis id=%s",
                        analysis_id,
                    )

                    add_job_event(
                        conn=conn,
                        job_id=job_id,
                        level="ERROR",
                        event_type="analysis_update_error",
                        message=(
                            "Error actualizando análisis "
                            f"{analysis_id}: {error}"
                        ),
                    )

                    conn.commit()

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
