from fastapi import APIRouter

from services.stats_service import StatsService


router = APIRouter(
    prefix="/api/stats",
    tags=["stats"],
)


@router.get("")
def stats():
    return StatsService.get_stats()


@router.get("/overview")
def statistics_overview():
    return StatsService.get_statistics()

@router.get("/geo")
def statistics_geo(classification: str = "all"):
    from fastapi import HTTPException

    if classification not in ("all", "malicious"):
        raise HTTPException(
            status_code=422,
            detail="classification debe ser 'all' o 'malicious'",
        )

    return StatsService.get_geo_statistics(classification)
