from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from sqlalchemy import select

from core.security.tokens import (
    create_access_token,
    create_refresh_token,
    hash_refresh_token,
)

from config import (
    ACCOUNT_LOCK_MINUTES,
    MAX_LOGIN_ATTEMPTS,
)
from core.security.passwords import (
    hash_password,
    needs_rehash,
    verify_password,
)
from core.security.tokens import (
    create_access_token,
    create_refresh_token,
)
from modules.audit.services.audit_service import (
    write_audit_log,
)
from modules.auth.models import RefreshToken
from modules.auth.repositories.user_repository import (
    get_user_by_id,
    get_user_by_login,
)


class AuthenticationError(Exception):
    pass


class AccountLockedError(Exception):
    pass


class InactiveAccountError(Exception):
    pass


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def authenticate_user(
    *,
    db: Session,
    login: str,
    password: str,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> dict:

    now = utc_now()

    user = get_user_by_login(
        db,
        login.strip(),
    )

    # Respuesta deliberadamente genérica.
    if user is None:
        write_audit_log(
            db=db,
            action="LOGIN_FAILED",
            result="FAILURE",
            username=login,
            resource_type="authentication",
            ip_address=ip_address,
            user_agent=user_agent,
            details={
                "reason": "invalid_credentials",
            },
        )

        db.commit()

        raise AuthenticationError(
            "Credenciales inválidas."
        )

    if not user.is_active:
        write_audit_log(
            db=db,
            action="LOGIN_FAILED",
            result="FAILURE",
            user_id=user.id,
            username=user.username,
            resource_type="authentication",
            ip_address=ip_address,
            user_agent=user_agent,
            details={
                "reason": "inactive_account",
            },
        )

        db.commit()

        raise InactiveAccountError(
            "Cuenta no disponible."
        )

    if (
        user.locked_until is not None
        and user.locked_until > now
    ):
        write_audit_log(
            db=db,
            action="LOGIN_BLOCKED",
            result="FAILURE",
            user_id=user.id,
            username=user.username,
            resource_type="authentication",
            ip_address=ip_address,
            user_agent=user_agent,
            details={
                "reason": "account_locked",
            },
        )

        db.commit()

        raise AccountLockedError(
            "Cuenta temporalmente bloqueada."
        )

    # Si el bloqueo ya expiró, reiniciamos estado.
    if (
        user.locked_until is not None
        and user.locked_until <= now
    ):
        user.locked_until = None
        user.failed_login_attempts = 0

    if not verify_password(
        password,
        user.password_hash,
    ):
        user.failed_login_attempts += 1

        locked = False

        if (
            user.failed_login_attempts
            >= MAX_LOGIN_ATTEMPTS
        ):
            user.locked_until = (
                now
                + timedelta(
                    minutes=ACCOUNT_LOCK_MINUTES
                )
            )
            locked = True

        user.updated_at = now

        write_audit_log(
            db=db,
            action=(
                "ACCOUNT_LOCKED"
                if locked
                else "LOGIN_FAILED"
            ),
            result="FAILURE",
            user_id=user.id,
            username=user.username,
            resource_type="authentication",
            ip_address=ip_address,
            user_agent=user_agent,
            details={
                "reason": "invalid_credentials",
                "failed_attempts":
                    user.failed_login_attempts,
                "locked": locked,
            },
        )

        db.commit()

        if locked:
            raise AccountLockedError(
                "Cuenta temporalmente bloqueada."
            )

        raise AuthenticationError(
            "Credenciales inválidas."
        )

    # Login correcto.
    user.failed_login_attempts = 0
    user.locked_until = None
    user.last_login_at = now
    user.updated_at = now

    # Rehash automático si cambian parámetros
    # Argon2 en el futuro.
    if needs_rehash(user.password_hash):
        user.password_hash = hash_password(
            password
        )
        user.password_changed_at = now

    roles = sorted(
        role.code
        for role in user.roles
    )

    access_token, expires_at = (
        create_access_token(
            user_id=user.id,
            username=user.username,
            roles=roles,
        )
    )

    (
        refresh_token,
        refresh_hash,
        refresh_expires_at,
    ) = create_refresh_token()

    db.add(
        RefreshToken(
            user_id=user.id,
            token_hash=refresh_hash,
            expires_at=refresh_expires_at,
            created_at=now,
            ip_address=ip_address,
            user_agent=user_agent,
        )
    )

    write_audit_log(
        db=db,
        action="LOGIN_SUCCESS",
        result="SUCCESS",
        user_id=user.id,
        username=user.username,
        resource_type="authentication",
        ip_address=ip_address,
        user_agent=user_agent,
        details={
            "roles": roles,
            "must_change_password":
                user.must_change_password,
        },
    )

    db.commit()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "expires_at": expires_at,
        "user": user,
        "roles": roles,
    }


class InvalidRefreshTokenError(Exception):
    pass


def rotate_refresh_token(
    *,
    db: Session,
    refresh_token: str,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> dict:

    now = utc_now()
    token_hash = hash_refresh_token(
        refresh_token
    )

    stored_token = db.execute(
        select(RefreshToken).where(
            RefreshToken.token_hash
            == token_hash
        )
    ).scalar_one_or_none()

    if stored_token is None:
        raise InvalidRefreshTokenError(
            "Refresh token inválido."
        )

    if stored_token.revoked_at is not None:
        raise InvalidRefreshTokenError(
            "Refresh token inválido."
        )

    if stored_token.expires_at <= now:
        raise InvalidRefreshTokenError(
            "Refresh token expirado."
        )

    user = get_user_by_id(
        db,
        stored_token.user_id,
    )

    if user is None or not user.is_active:
        raise InvalidRefreshTokenError(
            "Refresh token inválido."
        )

    # El token actual deja de ser utilizable.
    stored_token.revoked_at = now

    roles = sorted(
        role.code
        for role in user.roles
    )

    access_token, access_expires_at = (
        create_access_token(
            user_id=user.id,
            username=user.username,
            roles=roles,
        )
    )

    (
        new_refresh_token,
        new_refresh_hash,
        new_refresh_expires_at,
    ) = create_refresh_token()

    db.add(
        RefreshToken(
            user_id=user.id,
            token_hash=new_refresh_hash,
            expires_at=new_refresh_expires_at,
            created_at=now,
            ip_address=ip_address,
            user_agent=user_agent,
        )
    )

    write_audit_log(
        db=db,
        action="TOKEN_REFRESH",
        result="SUCCESS",
        user_id=user.id,
        username=user.username,
        resource_type="authentication",
        ip_address=ip_address,
        user_agent=user_agent,
        details={
            "rotation": True,
        },
    )

    db.commit()

    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "expires_at": access_expires_at,
    }


def revoke_refresh_token(
    *,
    db: Session,
    refresh_token: str,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> bool:

    now = utc_now()

    token_hash = hash_refresh_token(
        refresh_token
    )

    stored_token = db.execute(
        select(RefreshToken).where(
            RefreshToken.token_hash
            == token_hash
        )
    ).scalar_one_or_none()

    if stored_token is None:
        return False

    if stored_token.revoked_at is not None:
        return True

    stored_token.revoked_at = now

    user = get_user_by_id(
        db,
        stored_token.user_id,
    )

    write_audit_log(
        db=db,
        action="LOGOUT",
        result="SUCCESS",
        user_id=(
            user.id
            if user
            else stored_token.user_id
        ),
        username=(
            user.username
            if user
            else None
        ),
        resource_type="authentication",
        ip_address=ip_address,
        user_agent=user_agent,
    )

    db.commit()

    return True

class InvalidCurrentPasswordError(Exception):
    pass


class PasswordPolicyError(Exception):
    pass


def change_user_password(
    *,
    db: Session,
    user,
    current_password: str,
    new_password: str,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> None:

    if not verify_password(
        current_password,
        user.password_hash,
    ):
        write_audit_log(
            db=db,
            action="PASSWORD_CHANGE_FAILED",
            result="FAILURE",
            user_id=user.id,
            username=user.username,
            resource_type="authentication",
            ip_address=ip_address,
            user_agent=user_agent,
            details={
                "reason": "invalid_current_password",
            },
        )

        db.commit()

        raise InvalidCurrentPasswordError(
            "Contraseña actual inválida."
        )

    if len(new_password) < 12:
        raise PasswordPolicyError(
            "La nueva contraseña debe tener "
            "al menos 12 caracteres."
        )

    if verify_password(
        new_password,
        user.password_hash,
    ):
        raise PasswordPolicyError(
            "La nueva contraseña debe ser "
            "diferente a la actual."
        )

    now = utc_now()

    user.password_hash = hash_password(
        new_password
    )

    user.password_changed_at = now
    user.must_change_password = False
    user.failed_login_attempts = 0
    user.locked_until = None
    user.updated_at = now

    # Revocar todas las sesiones refresh
    # actualmente activas del usuario.
    active_tokens = db.execute(
        select(RefreshToken).where(
            RefreshToken.user_id == user.id,
            RefreshToken.revoked_at.is_(None),
        )
    ).scalars().all()

    revoked_count = 0

    for token in active_tokens:
        token.revoked_at = now
        revoked_count += 1

    write_audit_log(
        db=db,
        action="PASSWORD_CHANGED",
        result="SUCCESS",
        user_id=user.id,
        username=user.username,
        resource_type="authentication",
        ip_address=ip_address,
        user_agent=user_agent,
        details={
            "refresh_tokens_revoked":
                revoked_count,
        },
    )

    db.commit()