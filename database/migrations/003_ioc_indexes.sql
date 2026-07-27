-- ==========================================
-- IOC Platform
-- Migration: 003_ioc_indexes.sql
-- Description: Índices para mejorar el rendimiento del IOC Explorer
-- ==========================================

CREATE INDEX IF NOT EXISTS idx_iocs_tipo
ON iocs(tipo);

CREATE INDEX IF NOT EXISTS idx_iocs_fecha
ON iocs(fecha_creacion DESC);

CREATE INDEX IF NOT EXISTS idx_iocs_score
ON iocs(vt_score DESC);

CREATE INDEX IF NOT EXISTS idx_iocs_ultima_consulta
ON iocs(ultima_consulta DESC);

CREATE INDEX IF NOT EXISTS idx_iocs_tipo_estado
ON iocs(tipo, vt_estado);