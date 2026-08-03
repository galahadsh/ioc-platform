import logging
import time

from clients.virustotal import VirusTotalClient
from config import (
    COLLECTOR_BATCH_SIZE,
    VT_MAX_RETRIES,
)
from database import get_connection
from event_logger import add_event
from repositories.ioc_repository import (
    get_pending_iocs,
)
from runtime import (
    cancel_job,
    complete_job,
    create_baseline,
    fail_job,
    get_control_state,
    set_paused,
    set_running,
)
from services.analysis_service import update_analysis
from worker import process_single_ioc


logger = logging.getLogger("enrichment-engine")


class EnrichmentEngine:
    def __init__(
        self,
        job: dict,
    ) -> None:
        self.job = job
        self.job_id = int(job["id"])
        self.total_items = int(
            job["total_items"]
        )

        self.client = VirusTotalClient()

    def apply_control(
        self,
        conn,
    ) -> str:
        """
        Retorna:
            continue
            cancel
        """

        control = get_control_state(
            conn=conn,
            job_id=self.job_id,
        )

        if control is None:
            return "cancel"

        if control["cancel_requested"]:
            cancel_job(
                conn=conn,
                job_id=self.job_id,
            )

            conn.commit()
            return "cancel"

        if not control["pause_requested"]:
            return "continue"

        if control["status"] != "paused":
            set_paused(
                conn=conn,
                job_id=self.job_id,
            )

            conn.commit()

        logger.info(
            "Job %s pausado",
            self.job_id,
        )

        while True:
            time.sleep(2)

            control = get_control_state(
                conn=conn,
                job_id=self.job_id,
            )

            if control is None:
                return "cancel"

            if control["cancel_requested"]:
                cancel_job(
                    conn=conn,
                    job_id=self.job_id,
                )

                conn.commit()
                return "cancel"

            if not control["pause_requested"]:
                set_running(
                    conn=conn,
                    job_id=self.job_id,
                )

                conn.commit()
                return "continue"

    def update_analyses(
        self,
        conn,
        analysis_ids: set[int],
    ) -> None:
        for analysis_id in analysis_ids:
            try:
                update_analysis(
                    conn=conn,
                    analysis_id=analysis_id,
                )

                conn.commit()

            except Exception as error:
                conn.rollback()

                add_event(
                    conn=conn,
                    job_id=self.job_id,
                    level="ERROR",
                    event_type="analysis_update_error",
                    message=(
                        "Error actualizando analysis "
                        f"{analysis_id}: {error}"
                    ),
                )

                conn.commit()

    def run(self) -> None:
        conn = get_connection()

        try:
            create_baseline(
                conn=conn,
                job_id=self.job_id,
            )

            add_event(
                conn=conn,
                job_id=self.job_id,
                level="INFO",
                event_type="engine_ready",
                message=(
                    "Enrichment Engine listo. "
                    f"Batch={COLLECTOR_BATCH_SIZE} "
                    f"MaxRetries={VT_MAX_RETRIES}."
                ),
            )

            conn.commit()

            while True:
                if (
                    self.apply_control(conn)
                    == "cancel"
                ):
                    return

                pending_iocs = get_pending_iocs(
                    conn=conn,
                    limit=COLLECTOR_BATCH_SIZE,
                    max_retries=VT_MAX_RETRIES,
                )

                if not pending_iocs:
                    conn.rollback()
                    break

                analysis_ids: set[int] = set()

                for (
                    ioc_id,
                    analysis_id,
                    ioc_type,
                    value,
                    retry_count,
                    source,
                ) in pending_iocs:
                    if (
                        self.apply_control(conn)
                        == "cancel"
                    ):
                        return

                    process_single_ioc(
                        conn=conn,
                        client=self.client,
                        job_id=self.job_id,
                        total_items=self.total_items,
                        ioc_id=ioc_id,
                        ioc_type=ioc_type,
                        value=value,
                        retry_count=retry_count,
                        source=source,
                    )

                    if analysis_id is not None:
                        analysis_ids.add(
                            int(analysis_id)
                        )

                self.update_analyses(
                    conn=conn,
                    analysis_ids=analysis_ids,
                )

            complete_job(
                conn=conn,
                job_id=self.job_id,
            )

            conn.commit()

            logger.info(
                "Job %s completado",
                self.job_id,
            )

        except Exception as error:
            conn.rollback()

            logger.exception(
                "Job %s falló",
                self.job_id,
            )

            try:
                fail_job(
                    conn=conn,
                    job_id=self.job_id,
                    error=str(error),
                )

                conn.commit()

            except Exception:
                conn.rollback()

                logger.exception(
                    "No se pudo marcar job como failed"
                )

        finally:
            conn.close()
