from pathlib import Path
import os


BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "/uploads"))

DB_HOST = os.getenv("POSTGRES_HOST", "postgres")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB", "cyberintel")
DB_USER = os.getenv("POSTGRES_USER", "cyberintel")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")

DATABASE_URL = (
    f"postgresql://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
# ============================================================
# Security
# ============================================================

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

JWT_ALGORITHM = "HS256"

ACCESS_TOKEN_MINUTES = int(
    os.getenv(
        "ACCESS_TOKEN_MINUTES",
        "15",
    )
)

REFRESH_TOKEN_DAYS = int(
    os.getenv(
        "REFRESH_TOKEN_DAYS",
        "7",
    )
)

MAX_LOGIN_ATTEMPTS = int(
    os.getenv(
        "MAX_LOGIN_ATTEMPTS",
        "5",
    )
)

ACCOUNT_LOCK_MINUTES = int(
    os.getenv(
        "ACCOUNT_LOCK_MINUTES",
        "15",
    )
)

AUDIT_LOG_FILE = Path(
    os.getenv(
        "AUDIT_LOG_FILE",
        "/app/logs/audit.log",
    )
)
