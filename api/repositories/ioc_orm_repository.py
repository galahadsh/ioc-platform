from sqlalchemy import func, select
from sqlalchemy.orm import Session

from models.ioc import IOC


class IOCOrmRepository:
    def __init__(self, db: Session):
        self.db = db

    def count(self) -> int:
        statement = select(func.count(IOC.id))
        return self.db.scalar(statement) or 0

    def get_by_id(self, ioc_id: int) -> IOC | None:
        return self.db.get(IOC, ioc_id)

    def get_by_value(self, value: str) -> IOC | None:
        statement = select(IOC).where(IOC.valor == value)
        return self.db.scalar(statement)

    def list(
        self,
        *,
        limit: int = 100,
        offset: int = 0,
        tipo: str | None = None,
        estado: str | None = None,
    ) -> list[IOC]:
        statement = select(IOC)

        if tipo:
            statement = statement.where(IOC.tipo == tipo)

        if estado:
            statement = statement.where(IOC.vt_estado == estado)

        statement = (
            statement
            .order_by(IOC.fecha_creacion.desc(), IOC.id.desc())
            .limit(limit)
            .offset(offset)
        )

        return list(self.db.scalars(statement).all())

    def dashboard(self) -> dict[str, int]:
        return {
            "total_iocs": self.count(),
            "malicious": self.db.scalar(
                select(func.count(IOC.id)).where(
                    IOC.vt_estado == "malicious"
                )
            ) or 0,
            "suspicious": self.db.scalar(
                select(func.count(IOC.id)).where(
                    IOC.vt_estado == "suspicious"
                )
            ) or 0,
            "harmless": self.db.scalar(
                select(func.count(IOC.id)).where(
                    IOC.vt_estado == "harmless"
                )
            ) or 0,
            "undetected": self.db.scalar(
                select(func.count(IOC.id)).where(
                    IOC.vt_estado == "undetected"
                )
            ) or 0,
            "analizado": self.db.scalar(
                select(func.count(IOC.id)).where(
                    IOC.vt_estado == "analizado"
                )
            ) or 0,
            "errores": self.db.scalar(
                select(func.count(IOC.id)).where(
                    IOC.vt_estado == "error"
                )
            ) or 0,
        }

    from sqlalchemy import select

    def get_by_id(self, ioc_id: int):
        stmt = (
            select(IOC)
            .where(IOC.id == ioc_id)
        )

        return self.db.scalar(stmt)
