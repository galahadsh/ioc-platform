from sqlalchemy import or_, select
from sqlalchemy.orm import Session, selectinload

from modules.auth.models import Role, User


def get_user_by_id(
    db: Session,
    user_id: int,
) -> User | None:

    statement = (
        select(User)
        .options(
            selectinload(User.roles)
        )
        .where(
            User.id == user_id
        )
    )

    return db.execute(
        statement
    ).scalar_one_or_none()


def get_user_by_username(
    db: Session,
    username: str,
) -> User | None:

    statement = (
        select(User)
        .options(
            selectinload(User.roles)
        )
        .where(
            User.username == username
        )
    )

    return db.execute(
        statement
    ).scalar_one_or_none()


def get_user_by_login(
    db: Session,
    login: str,
) -> User | None:

    statement = (
        select(User)
        .options(
            selectinload(User.roles)
        )
        .where(
            or_(
                User.username == login,
                User.email == login,
            )
        )
    )

    return db.execute(
        statement
    ).scalar_one_or_none()


def get_role_by_code(
    db: Session,
    code: str,
) -> Role | None:

    statement = select(Role).where(
        Role.code == code
    )

    return db.execute(
        statement
    ).scalar_one_or_none()
