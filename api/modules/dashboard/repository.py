from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session

from models.ioc import IOC


class DashboardRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_summary(self) -> dict:
        total = self.db.scalar(
            select(func.count(IOC.id))
        ) or 0

        analyzed_condition = (
            IOC.vt_estado == "analizado"
        )

        malicious = self.db.scalar(
            select(func.count(IOC.id)).where(
                and_(
                    analyzed_condition,
                    func.coalesce(
                        IOC.vt_malicious,
                        0,
                    ) > 0,
                )
            )
        ) or 0

        suspicious = self.db.scalar(
            select(func.count(IOC.id)).where(
                and_(
                    analyzed_condition,
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

        clean = self.db.scalar(
            select(func.count(IOC.id)).where(
                and_(
                    analyzed_condition,
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

        analyzed = self.db.scalar(
            select(func.count(IOC.id)).where(
                analyzed_condition
            )
        ) or 0

        pending = self.db.scalar(
            select(func.count(IOC.id)).where(
                func.coalesce(
                    IOC.vt_estado,
                    "pendiente",
                ) == "pendiente"
            )
        ) or 0

        errors = self.db.scalar(
            select(func.count(IOC.id)).where(
                IOC.vt_estado == "error"
            )
        ) or 0

        return {
            "total": total,
            "analyzed": analyzed,
            "malicious": malicious,
            "suspicious": suspicious,
            "clean": clean,
            "pending": pending,
            "errors": errors,
        }

    def get_types(self) -> list[dict]:
        label = func.coalesce(
            IOC.tipo,
            "unknown",
        )

        statement = (
            select(
                label.label("label"),
                func.count(IOC.id).label("total"),
            )
            .group_by(label)
            .order_by(
                func.count(IOC.id).desc()
            )
        )

        rows = self.db.execute(
            statement
        ).mappings().all()

        return [dict(row) for row in rows]

    def get_sources(
        self,
        limit: int = 8,
    ) -> list[dict]:
        label = func.coalesce(
            IOC.fuente,
            "Sin fuente",
        )

        statement = (
            select(
                label.label("label"),
                func.count(IOC.id).label("total"),
            )
            .group_by(label)
            .order_by(
                func.count(IOC.id).desc()
            )
            .limit(limit)
        )

        rows = self.db.execute(
            statement
        ).mappings().all()

        return [dict(row) for row in rows]

    def get_campaigns(
        self,
        limit: int = 8,
    ) -> list[dict]:
        statement = (
            select(
                IOC.campaign.label("label"),
                func.count(IOC.id).label("total"),
            )
            .where(
                IOC.campaign.is_not(None),
                func.trim(IOC.campaign) != "",
            )
            .group_by(IOC.campaign)
            .order_by(
                func.count(IOC.id).desc()
            )
            .limit(limit)
        )

        rows = self.db.execute(
            statement
        ).mappings().all()

        return [dict(row) for row in rows]

    def get_malware(
        self,
        limit: int = 8,
    ) -> list[dict]:
        statement = (
            select(
                IOC.malware_family.label("label"),
                func.count(IOC.id).label("total"),
            )
            .where(
                IOC.malware_family.is_not(None),
                func.trim(
                    IOC.malware_family
                ) != "",
            )
            .group_by(IOC.malware_family)
            .order_by(
                func.count(IOC.id).desc()
            )
            .limit(limit)
        )

        rows = self.db.execute(
            statement
        ).mappings().all()

        return [dict(row) for row in rows]

    def get_monthly_activity(
        self,
        limit: int = 12,
    ) -> list[dict]:
        month = func.date_trunc(
            "month",
            IOC.fecha_creacion,
        )

        statement = (
            select(
                func.to_char(
                    month,
                    "YYYY-MM",
                ).label("label"),
                func.count(IOC.id).label("total"),
            )
            .where(
                IOC.fecha_creacion.is_not(None)
            )
            .group_by(month)
            .order_by(month.desc())
            .limit(limit)
        )

        rows = list(
            self.db.execute(
                statement
            ).mappings().all()
        )

        rows.reverse()

        return [dict(row) for row in rows]

    def get_recent_iocs(
        self,
        limit: int = 6,
    ) -> list[dict]:
        statement = (
            select(
                IOC.id,
                IOC.tipo,
                IOC.valor,
                IOC.vt_estado,
                IOC.vt_score,
                IOC.vt_malicious,
                IOC.campaign,
                IOC.malware_family,
                IOC.fuente,
                IOC.fecha_creacion,
                IOC.ultima_consulta,
            )
            .order_by(
                IOC.fecha_creacion.desc(),
                IOC.id.desc(),
            )
            .limit(limit)
        )

        rows = self.db.execute(
            statement
        ).mappings().all()

        return [dict(row) for row in rows]
