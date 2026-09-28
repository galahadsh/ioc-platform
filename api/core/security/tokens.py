import hashlib
import secrets
import uuid

from datetime import (
    datetime,
    timedelta,
    timezone,
)

import jwt

from config import (
    ACCESS_TOKEN_MINUTES,
    JWT_ALGORITHM,
    JWT_SECRET_KEY,
    REFRESH_TOKEN_DAYS,
)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def create_access_token(
    *,
    user_id: int,
    username: str,
    roles: list[str],
) -> tuple[str, datetime]:

    if not JWT_SECRET_KEY:
        raise RuntimeError(
            "JWT_SECRET_KEY no está configurado."
        )

    now = utc_now()

    expires_at = now + timedelta(
        minutes=ACCESS_TOKEN_MINUTES
    )

    payload = {
        "sub": str(user_id),
        "username": username,
        "roles": roles,
        "type": "access",
        "iat": now,
        "nbf": now,
        "exp": expires_at,
        "jti": str(uuid.uuid4()),
    }

    token = jwt.encode(
        payload,
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM,
    )

    return token, expires_at


def decode_access_token(token: str) -> dict:

    if not JWT_SECRET_KEY:
        raise RuntimeError(
            "JWT_SECRET_KEY no está configurado."
        )

    payload = jwt.decode(
        token,
        JWT_SECRET_KEY,
        algorithms=[JWT_ALGORITHM],
        options={
            "require": [
                "sub",
                "type",
                "iat",
                "exp",
                "jti",
            ],
        },
    )

    if payload.get("type") != "access":
        raise jwt.InvalidTokenError(
            "Tipo de token inválido."
        )

    return payload


def create_refresh_token() -> tuple[
    str,
    str,
    datetime,
]:
    """
    Devuelve:
      token sin cifrar -> solamente para el cliente
      hash SHA-256     -> almacenamiento en PostgreSQL
      fecha expiración
    """

    token = secrets.token_urlsafe(64)

    token_hash = hash_refresh_token(token)

    expires_at = utc_now() + timedelta(
        days=REFRESH_TOKEN_DAYS
    )

    return (
        token,
        token_hash,
        expires_at,
    )


def hash_refresh_token(token: str) -> str:
    return hashlib.sha256(
        token.encode("utf-8")
    ).hexdigest()
