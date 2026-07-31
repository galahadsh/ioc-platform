from sqlalchemy import and_, func, select
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
        statement = select(IOC).where(
            IOC.valor == value
        )

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
            statement = statement.where(
                func.lower(IOC.tipo) == tipo.lower()
            )

        if estado:
            statement = statement.where(
                func.lower(IOC.vt_estado) ==
                estado.lower()
            )

        statement = (
            statement
            .order_by(
                IOC.fecha_creacion.desc(),
                IOC.id.desc(),
            )
            .limit(limit)
            .offset(offset)
        )

        return list(
            self.db.scalars(statement).all()
        )

    def dashboard(self) -> dict[str, int]:
        total = self.count()

        maliciosos = self.db.scalar(
            select(func.count(IOC.id)).where(
                and_(
                    IOC.vt_estado == "analizado",
                    func.coalesce(
                        IOC.vt_malicious,
                        0,
                    ) > 0,
                )
            )
        ) or 0

        sospechosos = self.db.scalar(
            select(func.count(IOC.id)).where(
                and_(
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
            )
        ) or 0

        limpios = self.db.scalar(
            select(func.count(IOC.id)).where(
                and_(
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
            )
        ) or 0

        pendientes = self.db.scalar(
            select(func.count(IOC.id)).where(
                func.coalesce(
                    IOC.vt_estado,
                    "pendiente",
                ) == "pendiente"
            )
        ) or 0

        errores = self.db.scalar(
            select(func.count(IOC.id)).where(
                IOC.vt_estado == "error"
            )
        ) or 0

        analizados = self.db.scalar(
            select(func.count(IOC.id)).where(
                IOC.vt_estado == "analizado"
            )
        ) or 0

        return {
            "total_iocs": total,
            "malicious": maliciosos,
            "suspicious": sospechosos,
            "harmless": limpios,
            "undetected": pendientes,
            "analizado": analizados,
            "errores": errores,
        }
