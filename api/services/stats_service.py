from repositories.stats_repository import get_stats


class StatsService:
    @staticmethod
    def get_stats() -> dict:
        return get_stats()
