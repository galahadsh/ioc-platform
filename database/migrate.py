from pathlib import Path
import hashlib
import os

import psycopg2
from dotenv import load_dotenv


ROOT = Path(__file__).resolve().parent.parent

load_dotenv(ROOT / ".env")

MIGRATIONS = ROOT / "database" / "migrations"


conn = psycopg2.connect(
    host=os.getenv("POSTGRES_HOST", "postgres"),
    port=os.getenv("POSTGRES_PORT", "5432"),
    dbname=os.getenv("POSTGRES_DB"),
    user=os.getenv("POSTGRES_USER"),
    password=os.getenv("POSTGRES_PASSWORD"),
)

conn.autocommit = True

cur = conn.cursor()


cur.execute(
"""
CREATE TABLE IF NOT EXISTS schema_migrations(

version varchar PRIMARY KEY,

checksum varchar,

applied_at timestamp default now()

)
"""
)


cur.execute(
"""
SELECT version
FROM schema_migrations
"""
)

applied = {
    r[0]
    for r in cur.fetchall()
}


for file in sorted(MIGRATIONS.glob("*.sql")):

    version = file.name

    if version in applied:
        print(f"✓ {version}")
        continue

    print(f"Aplicando {version}")

    sql = file.read_text()

    cur.execute(sql)

    checksum = hashlib.sha256(
        file.read_bytes()
    ).hexdigest()

    cur.execute(
"""
INSERT INTO schema_migrations(
version,
checksum
)
VALUES(
%s,
%s
)
""",
(
version,
checksum
)
)

    print("OK")


cur.close()

conn.close()

print("Migraciones finalizadas.")
