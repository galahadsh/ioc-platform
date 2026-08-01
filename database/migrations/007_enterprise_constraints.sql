BEGIN;

CREATE INDEX IF NOT EXISTS idx_campaigns_name
    ON campaigns (name);

CREATE INDEX IF NOT EXISTS idx_campaigns_active
    ON campaigns (active);

CREATE INDEX IF NOT EXISTS idx_malware_name
    ON malware (name);

CREATE INDEX IF NOT EXISTS idx_threat_actors_name
    ON threat_actors (name);

CREATE INDEX IF NOT EXISTS idx_ioc_tags_ioc_id
    ON ioc_tags (ioc_id);

CREATE INDEX IF NOT EXISTS idx_ioc_tags_tag_id
    ON ioc_tags (tag_id);

CREATE INDEX IF NOT EXISTS idx_relationships_source
    ON ioc_relationships (source_ioc);

CREATE INDEX IF NOT EXISTS idx_relationships_target
    ON ioc_relationships (target_ioc);

CREATE INDEX IF NOT EXISTS idx_sightings_ioc_id
    ON sightings (ioc_id);

CREATE INDEX IF NOT EXISTS idx_sightings_seen_at
    ON sightings (seen_at DESC);

CREATE INDEX IF NOT EXISTS idx_case_iocs_case_id
    ON case_iocs (case_id);

CREATE INDEX IF NOT EXISTS idx_case_iocs_ioc_id
    ON case_iocs (ioc_id);

CREATE INDEX IF NOT EXISTS idx_sources_enabled
    ON sources (enabled);

CREATE INDEX IF NOT EXISTS idx_feeds_source_id
    ON feeds (source_id);

CREATE INDEX IF NOT EXISTS idx_ioc_types_name
    ON ioc_types (name);

COMMIT;
