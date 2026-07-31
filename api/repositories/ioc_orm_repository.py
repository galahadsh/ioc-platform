from datetime import date, datetime, time, timedelta
from typing import Any

from sqlalchemy import String, and_, asc, cast, desc, func, or_, select
from sqlalchemy.orm import Session

from models.ioc import IOC


ORDER_FIELDS = {
    "id": IOC.id,
    "tipo": IOC.tipo,
    "valor": IOC.valor,
    "estado": IOC.vt_estado,
    "score": IOC.vt_score,
    "fuente": IOC.fuente,
    "campaign": IOC.campaign,
    "malware_family": IOC.malware_family,
    "fecha_creacion": IOC.fecha_creacion,
    "ultima_consulta": IOC.ultima_consulta,
}


class IOCOrmRepository:
    def __init__(self, db: Session):
        self.db = db

    def count(self) -> int:
        statement = select(func.count(IOC.id))
        return self.db.scalar(statement) or 0

    def get_by_id(self, ioc_id: int) -> IOC | None:
        return self.db.get(IOC, ioc_id)

    def get_by_value(self, value: str) -> IOC | None:
        statement = select(IOC).where(
            IOC.valor == value
        )

        return self.db.scalar(statement)

    @staticmethod
    def _classification_condition(
        estado: str,
    ):
        normalized = estado.strip().lower()

        if normalized in {
            "malicious",
            "malicioso",
        }:
            return and_(
                IOC.vt_estado == "analizado",
                func.coalesce(
                    IOC.vt_malicious,
                    0,
                ) > 0,
            )

        if normalized in {
            "suspicious",
            "sospechoso",
        }:
            return and_(
                IOC.vt_estado == "analizado",
                func.coalesce(
                    IOC.vt_malicious,
                    0,
                ) == 0,
                func.coalesce(
                    IOC.vt_suspicious,
                    0,
                ) > 0,
            )

        if normalized in {
            "clean",
            "harmless",
            "limpio",
        }:
            return and_(
                IOC.vt_estado == "analizado",
                func.coalesce(
                    IOC.vt_malicious,
                    0,
                ) == 0,
                func.coalesce(
                    IOC.vt_suspicious,
                    0,
                ) == 0,
            )

        if normalized in {
            "pending",
            "pendiente",
        }:
            return func.coalesce(
                IOC.vt_estado,
                "pendiente",
            ) == "pendiente"

        if normalized in {
            "error",
            "errores",
        }:
            return IOC.vt_estado == "error"

        if normalized in {
            "analyzed",
            "analizado",
        }:
            return IOC.vt_estado == "analizado"

        return func.lower(
            IOC.vt_estado
        ) == normalized

    def _build_conditions(
        self,
        *,
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
    ) -> list[Any]:
        conditions: list[Any] = []

        if search and search.strip():
            value = f"%{search.strip()}%"

            conditions.append(
                or_(
                    IOC.valor.ilike(value),
                    IOC.tipo.ilike(value),
                    IOC.fuente.ilike(value),
                    IOC.campaign.ilike(value),
                    IOC.malware_family.ilike(value),
                    IOC.proveedor_reputacion.ilike(
                        value
                    ),
                    cast(
                        IOC.vt_score,
                        String,
                    ).ilike(value),
                )
            )

        if tipo and tipo.strip():
            conditions.append(
                func.lower(IOC.tipo) ==
                tipo.strip().lower()
            )

        if estado and estado.strip():
            conditions.append(
                self._classification_condition(
                    estado
                )
            )

        if fuente and fuente.strip():
            conditions.append(
                IOC.fuente.ilike(
                    f"%{fuente.strip()}%"
                )
            )

        if campaign and campaign.strip():
            conditions.append(
                IOC.campaign.ilike(
                    f"%{campaign.strip()}%"
                )
            )

        if (
            malware_family and
            malware_family.strip()
        ):
            conditions.append(
                IOC.malware_family.ilike(
                    f"%{malware_family.strip()}%"
                )
            )

        if score_min is not None:
            conditions.append(
                func.coalesce(
                    IOC.vt_score,
                    0,
                ) >= score_min
            )

        if score_max is not None:
            conditions.append(
                func.coalesce(
                    IOC.vt_score,
                    0,
                ) <= score_max
            )

        if date_from:
            conditions.append(
                IOC.fecha_creacion >= datetime.combine(
                    date_from,
                    time.min,
                )
            )

        if date_to:
            exclusive_end = (
                datetime.combine(
                    date_to,
                    time.min,
                ) +
                timedelta(days=1)
            )

            conditions.append(
                IOC.fecha_creacion <
                exclusive_end
            )

        return conditions

    def list_paginated(
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
    ) -> tuple[list[IOC], int]:
        conditions = self._build_conditions(
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
        )

        count_statement = select(
            func.count(IOC.id)
        )

        data_statement = select(IOC)

        if conditions:
            count_statement = (
                count_statement.where(
                    *conditions
                )
            )

            data_statement = (
                data_statement.where(
                    *conditions
                )
            )

        total = (
            self.db.scalar(
                count_statement
            ) or 0
        )

        order_column = ORDER_FIELDS.get(
            order_by,
            IOC.fecha_creacion,
        )

        ordering = (
            asc(order_column)
            if order_direction.lower() == "asc"
            else desc(order_column)
        )

        offset = (page - 1) * page_size

        data_statement = (
            data_statement
            .order_by(
                ordering,
                desc(IOC.id),
            )
            .limit(page_size)
            .offset(offset)
        )

        items = list(
            self.db.scalars(
                data_statement
            ).all()
        )

        return items, total

    def dashboard(self) -> dict[str, int]:
        total = self.count()

        malicious = self.db.scalar(
            select(func.count(IOC.id)).where(
                self._classification_condition(
                    "malicious"
                )
            )
        ) or 0

        suspicious = self.db.scalar(
            select(func.count(IOC.id)).where(
                self._classification_condition(
                    "suspicious"
                )
            )
        ) or 0

        clean = self.db.scalar(
            select(func.count(IOC.id)).where(
                self._classification_condition(
                    "clean"
                )
            )
        ) or 0

        pending = self.db.scalar(
            select(func.count(IOC.id)).where(
                self._classification_condition(
                    "pending"
                )
            )
        ) or 0

        errors = self.db.scalar(
            select(func.count(IOC.id)).where(
                IOC.vt_estado == "error"
            )
        ) or 0

        analyzed = self.db.scalar(
            select(func.count(IOC.id)).where(
                IOC.vt_estado == "analizado"
            )
        ) or 0

        return {
            "total_iocs": total,
            "malicious": malicious,
            "suspicious": suspicious,
            "harmless": clean,
            "undetected": pending,
            "analizado": analyzed,
            "errores": errors,
        }
