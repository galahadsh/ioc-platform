import logging

from psycopg2.extensions import connection

from clients.virustotal import VirusTotalClient
from event_logger import add_event
from repositories.ioc_repository import (
    get_ioc_result,
)
from runtime import (
    set_current_ioc,
    update_progress,
)
from services.enrichment_service import process_ioc


logger = logging.getLogger("ioc-worker")


def process_single_ioc(
    conn: connection,
    client: VirusTotalClient,
    job_id: int,
    total_items: int,
    ioc_id: int,
    ioc_type: str,
    value: str,
    retry_count: int,
    source: str | None,
) -> bool:
    """
    Procesa un IOC y registra runtime y eventos.
    """

    attempt = retry_count + 1

    progress_before = update_progress(
        conn=conn,
        job_id=job_id,
    )

    current_number = min(
        progress_before["processed"] + 1,
        total_items,
    )

    set_current_ioc(
        conn=conn,
        job_id=job_id,
        ioc_id=ioc_id,
        ioc_type=ioc_type,
        value=value,
        source=source,
        attempt=attempt,
    )

    add_event(
        conn=conn,
        job_id=job_id,
        level="INFO",
        event_type="ioc_started",
        ioc_id=ioc_id,
        message=(
            f"[{current_number}/{total_items}] "
            f"Consultando {value} "
            f"tipo={ioc_type} "
            f"intento={attempt}."
        ),
    )

    conn.commit()

    try:
        success = process_ioc(
            conn=conn,
            client=client,
            ioc_id=ioc_id,
            ioc_type=ioc_type,
            value=value,
            retry_count=retry_count,
        )

        result = get_ioc_result(
            conn=conn,
            ioc_id=ioc_id,
        ) or {}

        progress_after = update_progress(
            conn=conn,
            job_id=job_id,
        )

        if result.get("estado") == "analizado":
            add_event(
                conn=conn,
                job_id=job_id,
                level="INFO",
                event_type="ioc_analyzed",
                ioc_id=ioc_id,
                message=(
                    f"IOC analizado HTTP="
                    f"{result.get('http_code')}. "
                    f"Malicious="
                    f"{result.get('malicious', 0)} "
                    f"Suspicious="
                    f"{result.get('suspicious', 0)} "
                    f"Harmless="
                    f"{result.get('harmless', 0)} "
                    f"Undetected="
                    f"{result.get('undetected', 0)}."
                ),
            )

        elif result.get("estado") == "error":
            add_event(
                conn=conn,
                job_id=job_id,
                level="ERROR",
                event_type="ioc_error",
                ioc_id=ioc_id,
                message=(
                    f"IOC marcado como error. "
                    f"HTTP={result.get('http_code')} "
                    f"Detalle="
                    f"{result.get('error') or 'Sin detalle'}."
                ),
            )

        else:
            add_event(
                conn=conn,
                job_id=job_id,
                level="WARN",
                event_type="ioc_retry",
                ioc_id=ioc_id,
                message=(
                    "IOC pendiente de un nuevo intento. "
                    f"Retry={result.get('retry_count', 0)} "
                    f"HTTP={result.get('http_code')}."
                ),
            )

        add_event(
            conn=conn,
            job_id=job_id,
            level="DEBUG",
            event_type="progress",
            message=(
                f"Progreso "
                f"{progress_after['processed']}/"
                f"{total_items}. "
                f"Exitosos="
                f"{progress_after['successful']} "
                f"Fallidos="
                f"{progress_after['failed']}."
            ),
        )

        conn.commit()
        return success

    except Exception as error:
        conn.rollback()

        logger.exception(
            "Excepción procesando IOC id=%s",
            ioc_id,
        )

        add_event(
            conn=conn,
            job_id=job_id,
            level="ERROR",
            event_type="ioc_exception",
            ioc_id=ioc_id,
            message=(
                f"Excepción procesando {value}: "
                f"{error}"
            ),
        )

        conn.commit()
        return False
