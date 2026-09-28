from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    status,
)
from sqlalchemy.orm import Session

from database import get_db
from modules.auth.dependencies import require_roles
from modules.auth.models import User
from modules.auth.schemas.users import (
    UserAdminResponse,
    UserCreateRequest,
)
from modules.auth.services.user_admin_service import (
    InvalidRoleError,
    UserAlreadyExistsError,
    create_user,
)


router = APIRouter(
    prefix="/api/v1/admin/users",
    tags=["User Administration"],
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


def serialize_user(user: User) -> UserAdminResponse:
    return UserAdminResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        is_active=user.is_active,
        must_change_password=(
            user.must_change_password
        ),
        roles=sorted(
            role.code
            for role in user.roles
        ),
        created_at=user.created_at,
        last_login_at=user.last_login_at,
    )


@router.post(
    "",
    response_model=UserAdminResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_platform_user(
    payload: UserCreateRequest,
    request: Request,
    admin: User = Depends(
        require_roles("ADMIN")
    ),
    db: Session = Depends(get_db),
):
    try:
        user = create_user(
            db=db,
            username=payload.username,
            email=(
                str(payload.email)
                if payload.email
                else None
            ),
            full_name=payload.full_name,
            password=payload.password,
            role_codes=payload.roles,
            created_by=admin,
            ip_address=get_client_ip(request),
            user_agent=request.headers.get(
                "user-agent"
            ),
        )

    except UserAlreadyExistsError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        )

    except InvalidRoleError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )

    return serialize_user(user)
