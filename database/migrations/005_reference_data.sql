BEGIN;

INSERT INTO tags (
    name,
    color
)
VALUES
    ('APT', '#d32f2f'),
    ('Botnet', '#1976d2'),
    ('Phishing', '#7b1fa2'),
    ('Stealer', '#ef6c00'),
    ('Ransomware', '#c62828'),
    ('Malspam', '#6a1b9a'),
    ('C2', '#283593'),
    ('Scanner', '#00897b'),
    ('Cryptominer', '#455a64'),
    ('Bruteforce', '#5d4037')
ON CONFLICT (name) DO NOTHING;


INSERT INTO sources (
    name,
    type,
    enabled
)
VALUES
    ('VirusTotal', 'reputation', TRUE),
    ('AlienVault OTX', 'threat_feed', TRUE),
    ('Intel471', 'commercial_intelligence', TRUE),
    ('SOCradar', 'commercial_intelligence', TRUE),
    ('MISP', 'threat_intelligence_platform', TRUE),
    ('CSV', 'manual_import', TRUE),
    ('Manual', 'manual', TRUE),
    ('Splunk', 'siem', TRUE),
    ('TheHive', 'case_management', TRUE)
ON CONFLICT (name) DO NOTHING;

COMMIT;
