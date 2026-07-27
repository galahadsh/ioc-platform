CREATE TABLE IF NOT EXISTS analysis (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(255),
    total_iocs INTEGER DEFAULT 0,
    analizados INTEGER DEFAULT 0,
    maliciosos INTEGER DEFAULT 0,
    sospechosos INTEGER DEFAULT 0,
    limpios INTEGER DEFAULT 0,
    estado VARCHAR(50) DEFAULT 'pendiente',
    fecha_inicio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_fin TIMESTAMP
);


CREATE TABLE IF NOT EXISTS iocs (
    id SERIAL PRIMARY KEY,

    analysis_id INTEGER REFERENCES analysis(id),

    tipo VARCHAR(50) NOT NULL,
    valor TEXT NOT NULL,

    malicious INTEGER DEFAULT 0,
    suspicious INTEGER DEFAULT 0,
    harmless INTEGER DEFAULT 0,
    undetected INTEGER DEFAULT 0,

    proveedor_reputacion VARCHAR(100),

    vt_estado VARCHAR(50) DEFAULT 'pendiente',

    ultima_consulta TIMESTAMP,

    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE INDEX IF NOT EXISTS idx_iocs_estado
ON iocs(vt_estado);


CREATE INDEX IF NOT EXISTS idx_iocs_analysis
ON iocs(analysis_id);


