from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserCreateRequest(BaseModel):
    username: str = Field(
        min_length=3,
        max_length=100,
    )
    email: EmailStr | None = None
    full_name: str | None = Field(
        default=None,
        max_length=255,
    )
    password: str = Field(
        min_length=12,
        max_length=1024,
    )
    roles: list[str] = Field(
        min_length=1,
    )


class UserAdminResponse(BaseModel):
    id: int
    username: str
    email: str | None
    full_name: str | None
    is_active: bool
    must_change_password: bool
    roles: list[str]
    created_at: datetime
    last_login_at: datetime | None
