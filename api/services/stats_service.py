from repositories.stats_repository import get_stats


def get_dashboard_stats() -> dict:
    stats = get_stats()

    return {
        "total_iocs": stats["total"],
        "maliciosos": stats["maliciosos"],
        "sospechosos": stats["sospechosos"],
        "limpios": stats["limpios"],
        "pendientes": stats["pendientes"],
        "errores": stats["errores"],
    }