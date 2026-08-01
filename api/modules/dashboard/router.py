from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from modules.dashboard.schemas import (
    DashboardResponse,
)
from modules.dashboard.service import (
    DashboardService,
)


router = APIRouter(
    prefix="/api/v2/dashboard",
    tags=["Dashboard v2"],
)


@router.get(
    "",
    response_model=DashboardResponse,
)
def get_dashboard(
    db: Annotated[
        Session,
        Depends(get_db),
    ],
):
    service = DashboardService(db)

    return service.get_dashboard()
