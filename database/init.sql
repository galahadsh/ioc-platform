CREATE TABLE iocs (
    id SERIAL PRIMARY KEY,
    tipo VARCHAR(20) NOT NULL,
    valor TEXT NOT NULL UNIQUE,
    fuente VARCHAR(100),
    categoria VARCHAR(50),
    severidad VARCHAR(20),
    estado VARCHAR(20) DEFAULT 'activo',
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ultima_revision TIMESTAMP
);


CREATE TABLE reputacion (
    id SERIAL PRIMARY KEY,
    ioc_id INTEGER REFERENCES iocs(id),
    proveedor VARCHAR(50),
    resultado VARCHAR(50),
    score INTEGER,
    fecha_consulta TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE fuentes (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100),
    tipo VARCHAR(50),
    activo BOOLEAN DEFAULT TRUE
);
