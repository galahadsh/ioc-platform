import logging
import time

from psycopg2.extensions import connection

from clients.virustotal import VirusTotalClient
from config import (
    VT_MAX_RETRIES,
    VT_RATE_LIMIT_WAIT,
)
from repositories.ioc_repository import (
    increment_retry,
    mark_analyzed,
    mark_error,
)

logger = logging.getLogger(__name__)


def process_ioc(
    conn: connection,
    client: VirusTotalClient,
    ioc_id: int,
    ioc_type: str,
    value: str,
    retry_count: int,
) -> bool:
    """
    Procesa un IOC consultando VirusTotal.

    Returns:
        True  -> IOC analizado correctamente.
        False -> Error temporal o definitivo.
    """

    logger.info(
        "Procesando IOC id=%s tipo=%s valor=%s",
        ioc_id,
        ioc_type,
        value,
    )

    response = client.lookup(
        ioc_type,
        value,
    )

    # ==========================================
    # IOC analizado correctamente
    # ==========================================

    if response.success:

        attributes = response.attributes or {}

        stats = attributes.get(
            "last_analysis_stats",
            {},
        )

        mark_analyzed(
            conn=conn,
            ioc_id=ioc_id,
            stats=stats,
        )

        logger.info(
            (
                "IOC id=%s analizado "
                "malicious=%s suspicious=%s "
                "harmless=%s undetected=%s"
            ),
            ioc_id,
            stats.get("malicious", 0),
            stats.get("suspicious", 0),
            stats.get("harmless", 0),
            stats.get("undetected", 0),
        )

        return True

    # ==========================================
    # Error temporal
    # ==========================================

    next_retry = retry_count + 1

    if response.retryable and next_retry < VT_MAX_RETRIES:

        increment_retry(
            conn=conn,
            ioc_id=ioc_id,
            status_code=response.status_code,
            error=response.error or "Error temporal",
        )

        logger.warning(
            (
                "IOC id=%s error temporal "
                "http=%s intento=%s/%s "
                "motivo=%s"
            ),
            ioc_id,
            response.status_code,
            next_retry,
            VT_MAX_RETRIES,
            response.error,
        )

        if response.status_code == 429:
            logger.info(
                "Esperando %s segundos por Rate Limit...",
                VT_RATE_LIMIT_WAIT,
            )
            time.sleep(VT_RATE_LIMIT_WAIT)

        return False

    # ==========================================
    # Error definitivo
    # ==========================================

    final_error = response.error or "Error desconocido"

    if response.retryable:
        final_error = (
            f"{final_error}. "
            f"Máximo de reintentos alcanzado "
            f"({VT_MAX_RETRIES})"
        )

    mark_error(
        conn=conn,
        ioc_id=ioc_id,
        status_code=response.status_code,
        error=final_error,
    )

    logger.error(
        (
            "IOC id=%s marcado como ERROR "
            "http=%s motivo=%s"
        ),
        ioc_id,
        response.status_code,
        final_error,
    )

    return False