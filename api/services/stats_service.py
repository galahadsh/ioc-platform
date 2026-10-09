from repositories.stats_repository import (
    get_statistics,
    get_stats,
    get_iocs_by_country,
)


class StatsService:
    @staticmethod
    def get_stats() -> dict:
        return get_stats()

    @staticmethod
    def get_statistics() -> dict:
        return get_statistics()

    @staticmethod
    def get_geo_statistics(classification: str = "all") -> dict:
        countries = get_iocs_by_country(classification)

        return {
            "classification": classification,
            "total": sum(row["total"] for row in countries),
            "countries": countries,
        }
