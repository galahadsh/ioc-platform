from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from database import get_db


router = APIRouter(
    prefix="/api/enrichment",
    tags=["Enrichment"],
)


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
                  'running'
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
                "pendiente o en ejecución."
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
                total_items
            )
            VALUES (
                'virustotal',
                'pending',
                :total_items
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
    job = db.execute(
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
                error
            FROM enrichment_jobs
            WHERE provider = 'virustotal'
            ORDER BY created_at DESC
            LIMIT 1
            """
        )
    ).mappings().first()

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

    if job is None:
        return {
            "status": "idle",
            "message": (
                "No existen trabajos de "
                "VirusTotal registrados."
            ),
            "summary": dict(summary),
        }

    return {
        **dict(job),
        "summary": dict(summary),
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
              AND status IN ('pending', 'running')
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
