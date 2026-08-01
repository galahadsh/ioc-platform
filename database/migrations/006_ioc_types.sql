BEGIN;

CREATE TABLE IF NOT EXISTS ioc_types (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    display_name VARCHAR(100) NOT NULL,
    description TEXT,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

INSERT INTO ioc_types (
    name,
    display_name
)
VALUES
    ('ip', 'Dirección IP'),
    ('domain', 'Dominio'),
    ('url', 'URL'),
    ('md5', 'Hash MD5'),
    ('sha1', 'Hash SHA-1'),
    ('sha256', 'Hash SHA-256'),
    ('email', 'Correo electrónico'),
    ('asn', 'ASN'),
    ('cidr', 'Segmento CIDR'),
    ('filename', 'Nombre de archivo'),
    ('registry', 'Clave de registro'),
    ('mutex', 'Mutex'),
    ('yara', 'Regla YARA'),
    ('sigma', 'Regla Sigma')
ON CONFLICT (name) DO NOTHING;

COMMIT;
