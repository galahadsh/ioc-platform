from fastapi import APIRouter

from services.stats_service import get_dashboard_stats


router = APIRouter(prefix="/api", tags=["Statistics"])


@router.get("/stats")
def stats():
    return get_dashboard_stats()
