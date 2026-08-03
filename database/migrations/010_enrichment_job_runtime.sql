BEGIN;

ALTER TABLE enrichment_jobs
    ADD COLUMN IF NOT EXISTS current_ioc_id INTEGER,
    ADD COLUMN IF NOT EXISTS current_ioc_value TEXT,
    ADD COLUMN IF NOT EXISTS current_ioc_type VARCHAR(50),
    ADD COLUMN IF NOT EXISTS current_ioc_source TEXT,
    ADD COLUMN IF NOT EXISTS current_attempt INTEGER NOT NULL DEFAULT 0,
    ADD COLUMN IF NOT EXISTS max_attempts INTEGER NOT NULL DEFAULT 3,
    ADD COLUMN IF NOT EXISTS rate_limit_per_minute INTEGER NOT NULL DEFAULT 4,
    ADD COLUMN IF NOT EXISTS last_activity_at TIMESTAMP,
    ADD COLUMN IF NOT EXISTS pause_requested BOOLEAN NOT NULL DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS cancel_requested BOOLEAN NOT NULL DEFAULT FALSE;

CREATE INDEX IF NOT EXISTS idx_enrichment_jobs_last_activity
    ON enrichment_jobs (last_activity_at DESC);

COMMIT;
