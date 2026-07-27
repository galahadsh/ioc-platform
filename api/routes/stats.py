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