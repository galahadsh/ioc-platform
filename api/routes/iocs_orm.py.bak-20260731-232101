from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database import get_db
from repositories.ioc_orm_repository import IOCOrmRepository
from schemas.ioc_orm import IOCDetail, IOCResponse


router = APIRouter(
    prefix="/api/v2/iocs",
    tags=["IOCs v2"],
)


@router.get("", response_model=list[IOCResponse])
def list_iocs(
    db: Annotated[Session, Depends(get_db)],
    limit: Annotated[int, Query(ge=1, le=500)] = 100,
    offset: Annotated[int, Query(ge=0)] = 0,
    tipo: str | None = None,
    estado: str | None = None,
):
    repository = IOCOrmRepository(db)

    return repository.list(
        limit=limit,
        offset=offset,
        tipo=tipo,
        estado=estado,
    )


@router.get("/count")
def count_iocs(
    db: Annotated[Session, Depends(get_db)],
):
    repository = IOCOrmRepository(db)

    return {
        "total": repository.count(),
    }

@router.get("/dashboard")
def dashboard(
    db: Annotated[Session, Depends(get_db)],
):

    repo = IOCOrmRepository(db)

    return repo.dashboard()

@router.get(
    "/{ioc_id}",
    response_model=IOCDetail
)
def get_ioc(
    ioc_id: int,
    db: Session = Depends(get_db)
):
    repo = IOCOrmRepository(db)

    ioc = repo.get_by_id(ioc_id)

    if not ioc:
        raise HTTPException(
            status_code=404,
            detail="IOC no encontrado"
        )

    return ioc
