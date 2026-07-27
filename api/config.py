from pathlib import Path
import os


BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "/uploads"))

DB_HOST = os.getenv("POSTGRES_HOST", "postgres")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB", "cyberintel")
DB_USER = os.getenv("POSTGRES_USER", "cyberintel")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "SuperPassword123")

DATABASE_URL = (
    f"postgresql://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)