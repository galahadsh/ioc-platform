-- ============================================================
-- Cyber Intelligence Platform
-- Authentication, RBAC and Audit foundation
-- ============================================================

CREATE TABLE IF NOT EXISTS roles (
    id              SMALLSERIAL PRIMARY KEY,
    code            VARCHAR(50) NOT NULL UNIQUE,
    name            VARCHAR(100) NOT NULL,
    description     VARCHAR(255),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS users (
    id                  BIGSERIAL PRIMARY KEY,
    uuid                UUID NOT NULL UNIQUE,
    username            VARCHAR(100) NOT NULL UNIQUE,
    email               VARCHAR(255) UNIQUE,
    full_name           VARCHAR(255),
    password_hash       VARCHAR(512) NOT NULL,

    is_active           BOOLEAN NOT NULL DEFAULT TRUE,
    must_change_password BOOLEAN NOT NULL DEFAULT TRUE,

    failed_login_attempts INTEGER NOT NULL DEFAULT 0,
    locked_until        TIMESTAMPTZ,

    last_login_at       TIMESTAMPTZ,
    password_changed_at TIMESTAMPTZ,

    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS user_roles (
    user_id BIGINT NOT NULL
        REFERENCES users(id)
        ON DELETE CASCADE,

    role_id SMALLINT NOT NULL
        REFERENCES roles(id)
        ON DELETE CASCADE,

    assigned_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    PRIMARY KEY (user_id, role_id)
);

CREATE TABLE IF NOT EXISTS refresh_tokens (
    id              BIGSERIAL PRIMARY KEY,

    user_id         BIGINT NOT NULL
        REFERENCES users(id)
        ON DELETE CASCADE,

    token_hash      VARCHAR(64) NOT NULL UNIQUE,

    expires_at      TIMESTAMPTZ NOT NULL,
    revoked_at      TIMESTAMPTZ,

    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    ip_address      VARCHAR(64),
    user_agent      VARCHAR(512)
);

CREATE TABLE IF NOT EXISTS audit_events (
    id              BIGSERIAL PRIMARY KEY,

    event_uuid      UUID NOT NULL UNIQUE,

    occurred_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    user_id         BIGINT
        REFERENCES users(id)
        ON DELETE SET NULL,

    username        VARCHAR(100),

    action          VARCHAR(100) NOT NULL,
    resource_type   VARCHAR(100),
    resource_id     VARCHAR(255),

    result          VARCHAR(30) NOT NULL,

    ip_address      VARCHAR(64),
    user_agent      VARCHAR(512),
    request_id      UUID,

    details         JSONB,

    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_users_username
    ON users(username);

CREATE INDEX IF NOT EXISTS idx_users_email
    ON users(email);

CREATE INDEX IF NOT EXISTS idx_refresh_tokens_user
    ON refresh_tokens(user_id);

CREATE INDEX IF NOT EXISTS idx_refresh_tokens_expires
    ON refresh_tokens(expires_at);

CREATE INDEX IF NOT EXISTS idx_audit_events_occurred
    ON audit_events(occurred_at DESC);

CREATE INDEX IF NOT EXISTS idx_audit_events_user
    ON audit_events(user_id);

CREATE INDEX IF NOT EXISTS idx_audit_events_action
    ON audit_events(action);

CREATE INDEX IF NOT EXISTS idx_audit_events_result
    ON audit_events(result);

INSERT INTO roles (
    code,
    name,
    description
)
VALUES
(
    'ADMIN',
    'Administrador',
    'Administración completa de la plataforma.'
),
(
    'ANALYST',
    'Analista',
    'Operación y análisis de inteligencia.'
)
ON CONFLICT (code)
DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description;
