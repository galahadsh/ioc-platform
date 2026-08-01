from datetime import date
from typing import Annotated, Literal

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
)
from sqlalchemy.orm import Session

from database import get_db
from modules.iocs.repository import (
    IOCOrmRepository,
)
from modules.iocs.schemas import (
    IOCDetail,
    IOCListResponse,
)
from modules.iocs.service import IOCV2Service


router = APIRouter(
    prefix="/api/v2/iocs",
    tags=["IOCs v2"],
)


@router.get(
    "",
    response_model=IOCListResponse,
)
def list_iocs(
    db: Annotated[
        Session,
        Depends(get_db),
    ],
    page: Annotated[
        int,
        Query(ge=1),
    ] = 1,
    page_size: Annotated[
        int,
        Query(ge=10, le=200),
    ] = 25,
    search: str | None = None,
    tipo: str | None = None,
    estado: str | None = None,
    fuente: str | None = None,
    campaign: str | None = None,
    malware_family: str | None = None,
    score_min: Annotated[
        int | None,
        Query(ge=0),
    ] = None,
    score_max: Annotated[
        int | None,
        Query(ge=0),
    ] = None,
    date_from: date | None = None,
    date_to: date | None = None,
    order_by: Literal[
        "id",
        "tipo",
        "valor",
        "estado",
        "score",
        "fuente",
        "campaign",
        "malware_family",
        "fecha_creacion",
        "ultima_consulta",
    ] = "fecha_creacion",
    order_direction: Literal[
        "asc",
        "desc",
    ] = "desc",
):
    if (
        score_min is not None and
        score_max is not None and
        score_min > score_max
    ):
        raise HTTPException(
            status_code=400,
            detail=(
                "score_min no puede ser "
                "mayor que score_max."
            ),
        )

    if (
        date_from and
        date_to and
        date_from > date_to
    ):
        raise HTTPException(
            status_code=400,
            detail=(
                "date_from no puede ser "
                "mayor que date_to."
            ),
        )

    service = IOCV2Service(db)

    return service.list_iocs(
        page=page,
        page_size=page_size,
        search=search,
        tipo=tipo,
        estado=estado,
        fuente=fuente,
        campaign=campaign,
        malware_family=malware_family,
        score_min=score_min,
        score_max=score_max,
        date_from=date_from,
        date_to=date_to,
        order_by=order_by,
        order_direction=order_direction,
    )


@router.get("/count")
def count_iocs(
    db: Annotated[
        Session,
        Depends(get_db),
    ],
):
    repository = IOCOrmRepository(db)

    return {
        "total": repository.count(),
    }


@router.get("/dashboard")
def dashboard(
    db: Annotated[
        Session,
        Depends(get_db),
    ],
):
    repository = IOCOrmRepository(db)

    return repository.dashboard()


@router.get(
    "/{ioc_id}",
    response_model=IOCDetail,
)
def get_ioc(
    ioc_id: int,
    db: Annotated[
        Session,
        Depends(get_db),
    ],
):
    repository = IOCOrmRepository(db)
    ioc = repository.get_by_id(ioc_id)

    if ioc is None:
        raise HTTPException(
            status_code=404,
            detail="IOC no encontrado.",
        )

    return ioc
