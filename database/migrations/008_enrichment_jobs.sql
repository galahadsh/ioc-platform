BEGIN;

CREATE TABLE IF NOT EXISTS enrichment_jobs (
    id SERIAL PRIMARY KEY,
    provider VARCHAR(50) NOT NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'pending',

    total_items INTEGER NOT NULL DEFAULT 0,
    processed_items INTEGER NOT NULL DEFAULT 0,
    successful_items INTEGER NOT NULL DEFAULT 0,
    failed_items INTEGER NOT NULL DEFAULT 0,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    error TEXT
);

CREATE INDEX IF NOT EXISTS idx_enrichment_jobs_provider_status
    ON enrichment_jobs (
        provider,
        status
    );

CREATE INDEX IF NOT EXISTS idx_enrichment_jobs_created_at
    ON enrichment_jobs (
        created_at DESC
    );

COMMIT;
