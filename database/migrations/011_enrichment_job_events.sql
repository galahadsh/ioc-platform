BEGIN;

CREATE TABLE IF NOT EXISTS enrichment_job_events (
    id BIGSERIAL PRIMARY KEY,

    job_id INTEGER NOT NULL
        REFERENCES enrichment_jobs(id)
        ON DELETE CASCADE,

    level VARCHAR(20) NOT NULL DEFAULT 'INFO',
    event_type VARCHAR(80) NOT NULL DEFAULT 'general',
    message TEXT NOT NULL,

    ioc_id INTEGER,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_enrichment_events_job_id
    ON enrichment_job_events (
        job_id,
        id
    );

CREATE INDEX IF NOT EXISTS idx_enrichment_events_created_at
    ON enrichment_job_events (
        created_at DESC
    );

COMMIT;
