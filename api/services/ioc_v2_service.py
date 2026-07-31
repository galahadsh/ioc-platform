import math
from datetime import date

from sqlalchemy.orm import Session

from repositories.ioc_orm_repository import (
    IOCOrmRepository,
)


class IOCV2Service:
    def __init__(self, db: Session):
        self.repository = IOCOrmRepository(db)

    def list_iocs(
        self,
        *,
        page: int,
        page_size: int,
        search: str | None = None,
        tipo: str | None = None,
        estado: str | None = None,
        fuente: str | None = None,
        campaign: str | None = None,
        malware_family: str | None = None,
        score_min: int | None = None,
        score_max: int | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        order_by: str = "fecha_creacion",
        order_direction: str = "desc",
    ) -> dict:
        items, total = (
            self.repository.list_paginated(
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
        )

        total_pages = (
            math.ceil(total / page_size)
            if total
            else 0
        )

        return {
            "items": items,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total": total,
                "total_pages": total_pages,
                "has_previous": page > 1,
                "has_next":
                    page < total_pages,
            },
        }
