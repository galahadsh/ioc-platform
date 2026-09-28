import uuid

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from core.security.passwords import hash_password
from modules.audit.services.audit_service import (
    write_audit_log,
)
from modules.auth.models import Role, User


class UserAlreadyExistsError(Exception):
    pass


class InvalidRoleError(Exception):
    pass


def create_user(
    *,
    db: Session,
    username: str,
    email: str | None,
    full_name: str | None,
    password: str,
    role_codes: list[str],
    created_by: User,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> User:

    username = username.strip()

    normalized_email = (
        email.strip().lower()
        if email
        else None
    )

    normalized_roles = sorted({
        role.strip().upper()
        for role in role_codes
        if role.strip()
    })

    existing_conditions = [
        User.username == username,
    ]

    if normalized_email:
        existing_conditions.append(
            User.email == normalized_email
        )

    existing = db.execute(
        select(User).where(
            or_(*existing_conditions)
        )
    ).scalar_one_or_none()

    if existing:
        raise UserAlreadyExistsError(
            "El usuario o correo ya existe."
        )

    roles = db.execute(
        select(Role).where(
            Role.code.in_(normalized_roles)
        )
    ).scalars().all()

    found_roles = {
        role.code
        for role in roles
    }

    missing_roles = (
        set(normalized_roles)
        - found_roles
    )

    if missing_roles:
        raise InvalidRoleError(
            "Roles inválidos: "
            + ", ".join(
                sorted(missing_roles)
            )
        )

    if not roles:
        raise InvalidRoleError(
            "Debe asignarse al menos un rol."
        )

    user = User(
        uuid=uuid.uuid4(),
        username=username,
        email=normalized_email,
        full_name=(
            full_name.strip()
            if full_name
            else None
        ),
        password_hash=hash_password(password),
        is_active=True,
        must_change_password=True,
    )

    user.roles = roles

    db.add(user)
    db.flush()

    write_audit_log(
        db=db,
        action="USER_CREATED",
        result="SUCCESS",
        user_id=created_by.id,
        username=created_by.username,
        resource_type="user",
        resource_id=str(user.id),
        ip_address=ip_address,
        user_agent=user_agent,
        details={
            "created_user_id": user.id,
            "created_username": user.username,
            "roles": normalized_roles,
        },
    )

    db.commit()
    db.refresh(user)

    return user
