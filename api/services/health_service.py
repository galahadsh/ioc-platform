from datetime import datetime

START_TIME = datetime.now()


class HealthService:

    @staticmethod
    def get_health():

        uptime = datetime.now() - START_TIME

        hours = uptime.seconds // 3600
        minutes = (uptime.seconds % 3600) // 60

        return {
            "status": "ok",
            "database": "connected",
            "collector": "running",
            "api": "running",
            "version": "0.3.0",
            "uptime": f"{hours}h {minutes}m"
        }