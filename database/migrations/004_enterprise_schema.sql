-- ============================
-- CAMPAIGNS
-- ============================

CREATE TABLE IF NOT EXISTS campaigns (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) UNIQUE NOT NULL,
    description TEXT,
    first_seen TIMESTAMP,
    last_seen TIMESTAMP,
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ============================
-- MALWARE
-- ============================

CREATE TABLE IF NOT EXISTS malware (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) UNIQUE NOT NULL,
    family VARCHAR(200),
    platform VARCHAR(100),
    ransomware BOOLEAN DEFAULT FALSE,
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ============================
-- THREAT ACTORS
-- ============================

CREATE TABLE IF NOT EXISTS threat_actors (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) UNIQUE NOT NULL,
    alias VARCHAR(200),
    country VARCHAR(100),
    motivation VARCHAR(100),
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ============================
-- TAGS
-- ============================

CREATE TABLE IF NOT EXISTS tags (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    color VARCHAR(30) DEFAULT '#0d6efd'
);

-- ============================
-- IOC TAGS
-- ============================

CREATE TABLE IF NOT EXISTS ioc_tags (
    id SERIAL PRIMARY KEY,
    ioc_id INTEGER REFERENCES iocs(id) ON DELETE CASCADE,
    tag_id INTEGER REFERENCES tags(id) ON DELETE CASCADE,
    UNIQUE(ioc_id, tag_id)
);

-- ============================
-- IOC RELATIONSHIPS
-- ============================

CREATE TABLE IF NOT EXISTS ioc_relationships (
    id SERIAL PRIMARY KEY,
    source_ioc INTEGER REFERENCES iocs(id) ON DELETE CASCADE,
    target_ioc INTEGER REFERENCES iocs(id) ON DELETE CASCADE,
    relationship_type VARCHAR(100),
    confidence INTEGER DEFAULT 50,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ============================
-- SIGHTINGS
-- ============================

CREATE TABLE IF NOT EXISTS sightings (
    id SERIAL PRIMARY KEY,
    ioc_id INTEGER REFERENCES iocs(id) ON DELETE CASCADE,
    hostname VARCHAR(255),
    sensor VARCHAR(100),
    ip VARCHAR(100),
    seen_at TIMESTAMP DEFAULT NOW(),
    count INTEGER DEFAULT 1
);

-- ============================
-- CASES
-- ============================

CREATE TABLE IF NOT EXISTS cases (
    id SERIAL PRIMARY KEY,
    title VARCHAR(300) NOT NULL,
    status VARCHAR(50) DEFAULT 'Open',
    priority VARCHAR(50) DEFAULT 'Medium',
    created_at TIMESTAMP DEFAULT NOW()
);

-- ============================
-- CASE IOC
-- ============================

CREATE TABLE IF NOT EXISTS case_iocs (
    id SERIAL PRIMARY KEY,
    case_id INTEGER REFERENCES cases(id) ON DELETE CASCADE,
    ioc_id INTEGER REFERENCES iocs(id) ON DELETE CASCADE,
    UNIQUE(case_id, ioc_id)
);

-- ============================
-- SOURCES
-- ============================

CREATE TABLE IF NOT EXISTS sources (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) UNIQUE NOT NULL,
    type VARCHAR(100),
    enabled BOOLEAN DEFAULT TRUE
);

-- ============================
-- FEEDS
-- ============================

CREATE TABLE IF NOT EXISTS feeds (
    id SERIAL PRIMARY KEY,
    source_id INTEGER REFERENCES sources(id),
    name VARCHAR(200),
    url TEXT,
    enabled BOOLEAN DEFAULT TRUE,
    last_sync TIMESTAMP
);
