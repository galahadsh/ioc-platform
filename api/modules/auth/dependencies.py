import jwt

from fastapi import (
    Depends,
    HTTPException,
    status,
)
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)
from sqlalchemy.orm import Session

from core.security.tokens import decode_access_token
from database import get_db
from modules.auth.models import User
from modules.auth.repositories.user_repository import (
    get_user_by_id,
)


bearer_scheme = HTTPBearer(
    auto_error=False,
)


def get_current_user(
    credentials: HTTPAuthorizationCredentials
    | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:

    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token de autenticación inválido.",
        headers={
            "WWW-Authenticate": "Bearer",
        },
    )

    if credentials is None:
        raise unauthorized

    if credentials.scheme.lower() != "bearer":
        raise unauthorized

    try:
        payload = decode_access_token(
            credentials.credentials
        )

        user_id = int(payload["sub"])

    except (
        jwt.ExpiredSignatureError,
        jwt.InvalidTokenError,
        KeyError,
        TypeError,
        ValueError,
    ):
        raise unauthorized

    user = get_user_by_id(
        db,
        user_id,
    )

    if user is None:
        raise unauthorized

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cuenta no disponible.",
        )

    return user


def require_roles(*required_roles: str):
    required = set(required_roles)

    def dependency(
        user: User = Depends(
            get_current_user
        ),
    ) -> User:

        if user.must_change_password:
            raise HTTPException(
                status_code=(
                    status.HTTP_403_FORBIDDEN
                ),
                detail=(
                    "Debe cambiar su contraseña "
                    "antes de utilizar la plataforma."
                ),
            )

        user_roles = {
            role.code
            for role in user.roles
        }

        if not required.intersection(
            user_roles
        ):
            raise HTTPException(
                status_code=(
                    status.HTTP_403_FORBIDDEN
                ),
                detail=(
                    "No cuenta con permisos "
                    "para realizar esta acción."
                ),
            )

        return user

    return dependency

    def dependency(
        user: User = Depends(get_current_user),
    ) -> User:

        if user.must_change_password:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "Debe cambiar su contraseña "
                    "antes de utilizar la plataforma."
                ),
            )


def require_password_changed(
    user: User = Depends(get_current_user),
) -> User:
    if user.must_change_password:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Debe cambiar su contraseña "
                "antes de utilizar la plataforma."
            ),
        )

    return user
