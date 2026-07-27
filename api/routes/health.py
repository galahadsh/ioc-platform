from fastapi import APIRouter

from api.services.health_service import HealthService

router = APIRouter()


@router.get("/health")
async def health():

    return HealthService.get_health()