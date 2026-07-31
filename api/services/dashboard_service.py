from datetime import datetime, timezone

from sqlalchemy.orm import Session

from repositories.dashboard_repository import (
    DashboardRepository,
)


class DashboardService:
    def __init__(self, db: Session):
        self.repository = DashboardRepository(db)

    def get_dashboard(self) -> dict:
        summary = self.repository.get_summary()

        total = summary["total"]
        analyzed = summary["analyzed"]

        analyzed_percentage = (
            round((analyzed / total) * 100, 2)
            if total
            else 0
        )

        malicious_percentage = (
            round(
                (
                    summary["malicious"] /
                    analyzed
                ) * 100,
                2,
            )
            if analyzed
            else 0
        )

        return {
            "summary": {
                **summary,
                "analyzed_percentage":
                    analyzed_percentage,
                "malicious_percentage":
                    malicious_percentage,
            },
            "types":
                self.repository.get_types(),
            "sources":
                self.repository.get_sources(),
            "campaigns":
                self.repository.get_campaigns(),
            "malware":
                self.repository.get_malware(),
            "monthly":
                self.repository.get_monthly_activity(),
            "recent_iocs":
                self.repository.get_recent_iocs(),
            "generated_at":
                datetime.now(timezone.utc),
        }
