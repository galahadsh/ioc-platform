CREATE TABLE IF NOT EXISTS schema_migrations (

    version VARCHAR(100) PRIMARY KEY,

    checksum VARCHAR(64),

    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);
