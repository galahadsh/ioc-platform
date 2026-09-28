from datetime import datetime

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    login: str = Field(
        min_length=1,
        max_length=255,
    )

    password: str = Field(
        min_length=1,
        max_length=1024,
    )


class AuthUserResponse(BaseModel):
    id: int
    username: str
    email: str | None
    full_name: str | None
    roles: list[str]
    must_change_password: bool


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_at: datetime
    user: AuthUserResponse

class CurrentUserResponse(BaseModel):
    id: int
    username: str
    email: str | None
    full_name: str | None
    roles: list[str]
    must_change_password: bool
    last_login_at: datetime | None

class RefreshRequest(BaseModel):
    refresh_token: str = Field(
        min_length=32,
        max_length=1024,
    )


class RefreshResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_at: datetime


class LogoutRequest(BaseModel):
    refresh_token: str = Field(
        min_length=32,
        max_length=1024,
    )

class ChangePasswordRequest(BaseModel):
    current_password: str = Field(
        min_length=1,
        max_length=1024,
    )

    new_password: str = Field(
        min_length=12,
        max_length=1024,
    )