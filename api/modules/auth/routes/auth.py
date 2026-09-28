from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    status,
)
from sqlalchemy.orm import Session

from database import get_db
from modules.auth.dependencies import (
    get_current_user,
)
from modules.auth.models import User
from modules.auth.schemas import (
    AuthUserResponse,
    ChangePasswordRequest,
    CurrentUserResponse,
    LoginRequest,
    LoginResponse,
    LogoutRequest,
    RefreshRequest,
    RefreshResponse,
)
from modules.auth.services.auth_service import (
    AccountLockedError,
    AuthenticationError,
    InactiveAccountError,
    InvalidCurrentPasswordError,
    InvalidRefreshTokenError,
    PasswordPolicyError,
    authenticate_user,
    change_user_password,
    revoke_refresh_token,
    rotate_refresh_token,
)


router = APIRouter(
    prefix="/api/v1/auth",
    tags=["Authentication"],
)


def get_client_ip(request: Request) -> str | None:
    forwarded = request.headers.get(
        "x-forwarded-for"
    )

    if forwarded:
        return forwarded.split(",")[0].strip()

    if request.client:
        return request.client.host

    return None


@router.post(
    "/login",
    response_model=LoginResponse,
)
def login(
    payload: LoginRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    try:
        result = authenticate_user(
            db=db,
            login=payload.login,
            password=payload.password,
            ip_address=get_client_ip(request),
            user_agent=request.headers.get(
                "user-agent"
            ),
        )

    except AccountLockedError:
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail=(
                "Cuenta temporalmente bloqueada."
            ),
        )

    except InactiveAccountError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas.",
        )

    except AuthenticationError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas.",
        )

    user = result["user"]

    return LoginResponse(
        access_token=result["access_token"],
        refresh_token=result["refresh_token"],
        expires_at=result["expires_at"],
        user=AuthUserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            roles=result["roles"],
            must_change_password=(
                user.must_change_password
            ),
        ),
    )
@router.get(
    "/me",
    response_model=CurrentUserResponse,
)
def me(
    user: User = Depends(
        get_current_user
    ),
):
    roles = sorted(
        role.code
        for role in user.roles
    )

    return CurrentUserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        roles=roles,
        must_change_password=(
            user.must_change_password
        ),
        last_login_at=user.last_login_at,
    )

@router.post(
    "/refresh",
    response_model=RefreshResponse,
)
def refresh(
    payload: RefreshRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    try:
        result = rotate_refresh_token(
            db=db,
            refresh_token=payload.refresh_token,
            ip_address=get_client_ip(request),
            user_agent=request.headers.get(
                "user-agent"
            ),
        )

    except InvalidRefreshTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token inválido.",
        )

    return RefreshResponse(
        access_token=result["access_token"],
        refresh_token=result["refresh_token"],
        expires_at=result["expires_at"],
    )


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
)
def logout(
    payload: LogoutRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    revoke_refresh_token(
        db=db,
        refresh_token=payload.refresh_token,
        ip_address=get_client_ip(request),
        user_agent=request.headers.get(
            "user-agent"
        ),
    )

    return None

@router.post(
    "/change-password",
    status_code=status.HTTP_204_NO_CONTENT,
)
def change_password(
    payload: ChangePasswordRequest,
    request: Request,
    user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
):
    try:
        change_user_password(
            db=db,
            user=user,
            current_password=(
                payload.current_password
            ),
            new_password=(
                payload.new_password
            ),
            ip_address=get_client_ip(request),
            user_agent=request.headers.get(
                "user-agent"
            ),
        )

    except InvalidCurrentPasswordError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Contraseña actual inválida.",
        )

    except PasswordPolicyError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )

    return None


@router.post(
    "/change-password",
    status_code=status.HTTP_204_NO_CONTENT,
)
def change_password(
    payload: ChangePasswordRequest,
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        change_user_password(
            db=db,
            user=user,
            current_password=payload.current_password,
            new_password=payload.new_password,
            ip_address=get_client_ip(request),
            user_agent=request.headers.get(
                "user-agent"
            ),
        )

    except InvalidCurrentPasswordError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Contraseña actual inválida.",
        )

    except PasswordPolicyError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )

    return None
