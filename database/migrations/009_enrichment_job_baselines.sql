BEGIN;

CREATE TABLE IF NOT EXISTS enrichment_job_baselines (
    job_id INTEGER PRIMARY KEY
        REFERENCES enrichment_jobs(id)
        ON DELETE CASCADE,

    analyzed_at_start INTEGER NOT NULL DEFAULT 0,
    errors_at_start INTEGER NOT NULL DEFAULT 0
);

COMMIT;
