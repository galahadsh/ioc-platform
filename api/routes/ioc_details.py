from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from services.ioc_v2_service import IOCV2Service

router = APIRouter(
    prefix="/api/v2/iocs",
    tags=["IOC Explorer"],
)


@router.get("/{ioc_id}/details")
def get_ioc_details(
    ioc_id: int,
    db: Session = Depends(get_db),
):
    service = IOCV2Service(db)

    data = service.get_details(ioc_id)

    if data is None:
        raise HTTPException(
            status_code=404,
            detail="IOC no encontrado",
        )

    return data
