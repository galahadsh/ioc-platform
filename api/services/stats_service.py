from repositories.stats_repository import (
    get_statistics,
    get_stats,
)


class StatsService:
    @staticmethod
    def get_stats() -> dict:
        return get_stats()

    @staticmethod
    def get_statistics() -> dict:
        return get_statistics()
