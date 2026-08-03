from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.orm import Session

from database import get_db


router = APIRouter(
    prefix="/api/enrichment",
    tags=["Enrichment"],
)


ACTIVE_STATUSES = (
    "pending",
    "running",
    "paused",
)


def seconds_between(
    start: datetime | None,
    end: datetime | None = None,
) -> int:
    if start is None:
        return 0

    if end is None:
        end = datetime.now(timezone.utc)

    if start.tzinfo is None:
        start = start.replace(
            tzinfo=timezone.utc
        )

    if end.tzinfo is None:
        end = end.replace(
            tzinfo=timezone.utc
        )

    return max(
        int((end - start).total_seconds()),
        0,
    )


def serialize_job(job: dict) -> dict:
    total = int(job.get("total_items") or 0)
    processed = int(
        job.get("processed_items") or 0
    )

    percentage = (
        round(processed / total * 100, 2)
        if total
        else 0
    )

    status = job.get("status", "idle")

    elapsed_end = (
        job.get("completed_at")
        if status in {
            "completed",
            "failed",
            "cancelled",
        }
        else None
    )

    elapsed_seconds = seconds_between(
        job.get("started_at"),
        elapsed_end,
    )

    remaining_items = max(
        total - processed,
        0,
    )

    if processed > 0 and elapsed_seconds > 0:
        average_seconds = (
            elapsed_seconds / processed
        )

        estimated_remaining = int(
            average_seconds * remaining_items
        )
    else:
        estimated_remaining = 0

    return {
        **job,
        "percentage": percentage,
        "elapsed_seconds": elapsed_seconds,
        "estimated_remaining_seconds":
            estimated_remaining,
        "remaining_items": remaining_items,
        "current_item": {
            "id": job.get("current_ioc_id"),
            "tipo": job.get(
                "current_ioc_type"
            ),
            "valor": job.get(
                "current_ioc_value"
            ),
            "fuente": job.get(
                "current_ioc_source"
            ),
            "attempt": job.get(
                "current_attempt"
            ) or 0,
            "max_attempts": job.get(
                "max_attempts"
            ) or 3,
        },
    }


def get_latest_job(
    db: Session,
) -> dict | None:
    row = db.execute(
        text(
            """
            SELECT
                id,
                provider,
                status,
                total_items,
                processed_items,
                successful_items,
                failed_items,
                created_at,
                started_at,
                completed_at,
                error,

                current_ioc_id,
                current_ioc_value,
                current_ioc_type,
                current_ioc_source,
                current_attempt,
                max_attempts,
                rate_limit_per_minute,
                last_activity_at,
                pause_requested,
                cancel_requested

            FROM enrichment_jobs
            WHERE provider = 'virustotal'
            ORDER BY created_at DESC
            LIMIT 1
            """
        )
    ).mappings().first()

    return dict(row) if row else None


@router.get("/virustotal/summary")
def get_virustotal_summary(
    db: Annotated[Session, Depends(get_db)],
):
    row = db.execute(
        text(
            """
            SELECT
                COUNT(*) AS total,

                COUNT(*) FILTER (
                    WHERE vt_estado = 'pendiente'
                ) AS pending,

                COUNT(*) FILTER (
                    WHERE vt_estado = 'analizado'
                ) AS analyzed,

                COUNT(*) FILTER (
                    WHERE vt_estado = 'error'
                ) AS errors

            FROM iocs
            """
        )
    ).mappings().one()

    return dict(row)


@router.post("/virustotal/start")
def start_virustotal_analysis(
    db: Annotated[Session, Depends(get_db)],
):
    active_job = db.execute(
        text(
            """
            SELECT
                id,
                status
            FROM enrichment_jobs
            WHERE provider = 'virustotal'
              AND status IN (
                  'pending',
                  'running',
                  'paused'
              )
            ORDER BY created_at DESC
            LIMIT 1
            """
        )
    ).mappings().first()

    if active_job is not None:
        return {
            "started": False,
            "message": (
                "Ya existe un análisis de VirusTotal "
                "pendiente, activo o pausado."
            ),
            "job_id": active_job["id"],
            "status": active_job["status"],
        }

    pending = db.execute(
        text(
            """
            SELECT COUNT(*)
            FROM iocs
            WHERE vt_estado = 'pendiente'
            """
        )
    ).scalar_one()

    if pending == 0:
        return {
            "started": False,
            "message": (
                "No existen IOC pendientes "
                "de análisis en VirusTotal."
            ),
            "pending": 0,
        }

    job_id = db.execute(
        text(
            """
            INSERT INTO enrichment_jobs (
                provider,
                status,
                total_items,
                max_attempts,
                rate_limit_per_minute
            )
            VALUES (
                'virustotal',
                'pending',
                :total_items,
                3,
                4
            )
            RETURNING id
            """
        ),
        {
            "total_items": pending,
        },
    ).scalar_one()

    db.commit()

    return {
        "started": True,
        "message": (
            "El análisis fue agregado a la cola. "
            "El collector comenzará a procesarlo."
        ),
        "job_id": job_id,
        "pending": pending,
    }


@router.get("/virustotal/status")
def get_virustotal_status(
    db: Annotated[Session, Depends(get_db)],
):
    summary = db.execute(
        text(
            """
            SELECT
                COUNT(*) FILTER (
                    WHERE vt_estado = 'pendiente'
                ) AS pending,

                COUNT(*) FILTER (
                    WHERE vt_estado = 'analizado'
                ) AS analyzed,

                COUNT(*) FILTER (
                    WHERE vt_estado = 'error'
                ) AS errors

            FROM iocs
            """
        )
    ).mappings().one()

    job = get_latest_job(db)

    if job is None:
        return {
            "status": "idle",
            "message": (
                "No existen trabajos de "
                "VirusTotal registrados."
            ),
            "summary": dict(summary),
            "percentage": 0,
            "elapsed_seconds": 0,
            "estimated_remaining_seconds": 0,
            "current_item": None,
        }

    return {
        **serialize_job(job),
        "summary": dict(summary),
    }


@router.get("/virustotal/events")
def get_virustotal_events(
    db: Annotated[Session, Depends(get_db)],
    after_id: Annotated[
        int,
        Query(ge=0),
    ] = 0,
    limit: Annotated[
        int,
        Query(ge=1, le=500),
    ] = 200,
):
    job = get_latest_job(db)

    if job is None:
        return {
            "job_id": None,
            "events": [],
            "last_event_id": after_id,
        }

    rows = db.execute(
        text(
            """
            SELECT
                id,
                job_id,
                level,
                event_type,
                message,
                ioc_id,
                created_at
            FROM enrichment_job_events
            WHERE job_id = :job_id
              AND id > :after_id
            ORDER BY id
            LIMIT :limit
            """
        ),
        {
            "job_id": job["id"],
            "after_id": after_id,
            "limit": limit,
        },
    ).mappings().all()

    events = [
        dict(row)
        for row in rows
    ]

    last_event_id = (
        events[-1]["id"]
        if events
        else after_id
    )

    return {
        "job_id": job["id"],
        "events": events,
        "last_event_id": last_event_id,
    }


@router.post("/virustotal/pause")
def pause_virustotal_analysis(
    db: Annotated[Session, Depends(get_db)],
):
    job = get_latest_job(db)

    if job is None or job["status"] != "running":
        raise HTTPException(
            status_code=409,
            detail=(
                "No existe un análisis activo "
                "que pueda pausarse."
            ),
        )

    db.execute(
        text(
            """
            UPDATE enrichment_jobs
            SET
                pause_requested = TRUE,
                last_activity_at = CURRENT_TIMESTAMP
            WHERE id = :job_id
            """
        ),
        {
            "job_id": job["id"],
        },
    )

    db.commit()

    return {
        "message": (
            "Solicitud de pausa enviada. "
            "El collector se detendrá después "
            "del IOC actual."
        ),
        "job_id": job["id"],
    }


@router.post("/virustotal/resume")
def resume_virustotal_analysis(
    db: Annotated[Session, Depends(get_db)],
):
    job = get_latest_job(db)

    if job is None or job["status"] != "paused":
        raise HTTPException(
            status_code=409,
            detail=(
                "No existe un análisis pausado "
                "que pueda reanudarse."
            ),
        )

    db.execute(
        text(
            """
            UPDATE enrichment_jobs
            SET
                pause_requested = FALSE,
                last_activity_at = CURRENT_TIMESTAMP
            WHERE id = :job_id
            """
        ),
        {
            "job_id": job["id"],
        },
    )

    db.commit()

    return {
        "message": "Solicitud de reanudación enviada.",
        "job_id": job["id"],
    }


@router.post("/virustotal/cancel")
def cancel_virustotal_analysis(
    db: Annotated[Session, Depends(get_db)],
):
    job = get_latest_job(db)

    if (
        job is None or
        job["status"] not in ACTIVE_STATUSES
    ):
        raise HTTPException(
            status_code=409,
            detail=(
                "No existe un análisis activo "
                "que pueda cancelarse."
            ),
        )

    db.execute(
        text(
            """
            UPDATE enrichment_jobs
            SET
                cancel_requested = TRUE,
                pause_requested = FALSE,
                last_activity_at = CURRENT_TIMESTAMP
            WHERE id = :job_id
            """
        ),
        {
            "job_id": job["id"],
        },
    )

    db.commit()

    return {
        "message": (
            "Solicitud de cancelación enviada. "
            "Los IOC pendientes permanecerán "
            "sin analizar."
        ),
        "job_id": job["id"],
    }


@router.delete("/virustotal/events")
def clear_virustotal_events(
    db: Annotated[Session, Depends(get_db)],
):
    job = get_latest_job(db)

    if job is None:
        return {
            "deleted": 0,
            "message": "No existen eventos que eliminar.",
        }

    result = db.execute(
        text(
            """
            DELETE FROM enrichment_job_events
            WHERE job_id = :job_id
            """
        ),
        {
            "job_id": job["id"],
        },
    )

    db.commit()

    return {
        "deleted": result.rowcount,
        "message": (
            "Eventos del trabajo actual eliminados."
        ),
    }


@router.post("/virustotal/retry-errors")
def retry_virustotal_errors(
    db: Annotated[Session, Depends(get_db)],
):
    active_job = db.execute(
        text(
            """
            SELECT id
            FROM enrichment_jobs
            WHERE provider = 'virustotal'
              AND status IN (
                  'pending',
                  'running',
                  'paused'
              )
            LIMIT 1
            """
        )
    ).scalar_one_or_none()

    if active_job is not None:
        raise HTTPException(
            status_code=409,
            detail=(
                "No se pueden reiniciar errores "
                "mientras existe un análisis activo."
            ),
        )

    result = db.execute(
        text(
            """
            UPDATE iocs
            SET
                vt_estado = 'pendiente',
                vt_retry_count = 0,
                vt_http_code = NULL,
                vt_error = NULL
            WHERE vt_estado = 'error'
            """
        )
    )

    db.commit()

    return {
        "message": (
            "Los IOC con error fueron enviados "
            "nuevamente a pendientes."
        ),
        "updated": result.rowcount,
    }
