BEGIN;

CREATE TABLE IF NOT EXISTS document_status (
    id SMALLSERIAL PRIMARY KEY,
    code VARCHAR(30) NOT NULL UNIQUE,
    name VARCHAR(60) NOT NULL,
    description TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

INSERT INTO document_status (
    code,
    name,
    description
)
VALUES
    (
        'UPLOADED',
        'Uploaded',
        'Documento almacenado correctamente'
    ),
    (
        'QUEUED',
        'Queued',
        'Documento pendiente de procesamiento'
    ),
    (
        'PROCESSING',
        'Processing',
        'Documento en procesamiento'
    ),
    (
        'PROCESSED',
        'Processed',
        'Procesamiento básico completado'
    ),
    (
        'CORRELATED',
        'Correlated',
        'Correlación de inteligencia completada'
    ),
    (
        'ARCHIVED',
        'Archived',
        'Documento archivado'
    ),
    (
        'ERROR',
        'Error',
        'El procesamiento terminó con error'
    )
ON CONFLICT (code) DO NOTHING;


CREATE TABLE IF NOT EXISTS documents (
    id BIGSERIAL PRIMARY KEY,

    uuid UUID NOT NULL UNIQUE,

    original_name VARCHAR(512) NOT NULL,

    stored_name VARCHAR(512) NOT NULL,

    bucket VARCHAR(255) NOT NULL,

    object_name VARCHAR(1024) NOT NULL,

    content_type VARCHAR(255),

    extension VARCHAR(50),

    size_bytes BIGINT NOT NULL,

    sha256 CHAR(64) NOT NULL,

    md5 CHAR(32) NOT NULL,

    source VARCHAR(255),

    tlp VARCHAR(30),

    classification VARCHAR(100),

    status_id SMALLINT NOT NULL
        REFERENCES document_status(id),

    uploaded_by VARCHAR(255),

    uploaded_at TIMESTAMP NOT NULL
        DEFAULT NOW(),

    processed_at TIMESTAMP,

    updated_at TIMESTAMP NOT NULL
        DEFAULT NOW(),

    error_message TEXT,

    CONSTRAINT uq_documents_storage
        UNIQUE (
            bucket,
            object_name
        )
);

CREATE INDEX IF NOT EXISTS
    ix_documents_sha256
ON documents (
    sha256
);

CREATE INDEX IF NOT EXISTS
    ix_documents_status_id
ON documents (
    status_id
);

CREATE INDEX IF NOT EXISTS
    ix_documents_uploaded_at
ON documents (
    uploaded_at DESC
);

CREATE INDEX IF NOT EXISTS
    ix_documents_source
ON documents (
    source
);

COMMIT;
