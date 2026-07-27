import os


VT_API_KEY = os.getenv("VT_API_KEY")

VT_BASE_URL = os.getenv(
    "VT_BASE_URL",
    "https://www.virustotal.com/api/v3",
)

VT_REQUEST_TIMEOUT = int(
    os.getenv("VT_REQUEST_TIMEOUT", "30")
)

VT_RATE_LIMIT_WAIT = int(
    os.getenv("VT_RATE_LIMIT_WAIT", "60")
)

VT_MAX_RETRIES = int(
    os.getenv("VT_MAX_RETRIES", "3")
)

COLLECTOR_BATCH_SIZE = int(
    os.getenv("COLLECTOR_BATCH_SIZE", "10")
)

COLLECTOR_INTERVAL = int(
    os.getenv("COLLECTOR_INTERVAL", "30")
)

DB_CONFIG = {
    "host": os.getenv("POSTGRES_HOST", "postgres"),
    "database": os.getenv("POSTGRES_DB", "cyberintel"),
    "user": os.getenv("POSTGRES_USER", "cyberintel"),
    "password": os.getenv("POSTGRES_PASSWORD"),
    "port": int(os.getenv("POSTGRES_PORT", "5432")),
}


def validate_config() -> None:
    missing = []

    if not VT_API_KEY:
        missing.append("VT_API_KEY")

    if not DB_CONFIG["password"]:
        missing.append("POSTGRES_PASSWORD")

    if missing:
        raise RuntimeError(
            "Faltan variables obligatorias: "
            + ", ".join(missing)
        )
