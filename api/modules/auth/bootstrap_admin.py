import getpass
import sys
import uuid

from datetime import datetime, timezone

from sqlalchemy import or_, select

from core.security.passwords import hash_password
from database import SessionLocal
from modules.audit.services.audit_service import (
    write_audit_log,
)
from modules.auth.models import Role, User


MIN_PASSWORD_LENGTH = 12


def prompt_required(label: str) -> str:
    while True:
        value = input(label).strip()

        if value:
            return value

        print("Este campo es obligatorio.")


def get_password() -> str:
    while True:
        password = getpass.getpass(
            "Contraseña: "
        )

        confirmation = getpass.getpass(
            "Confirmar contraseña: "
        )

        if password != confirmation:
            print(
                "Las contraseñas no coinciden."
            )
            continue

        if len(password) < MIN_PASSWORD_LENGTH:
            print(
                "La contraseña debe tener "
                f"al menos {MIN_PASSWORD_LENGTH} "
                "caracteres."
            )
            continue

        return password


def main() -> None:
    print()
    print(
        "=== IOC Platform - Bootstrap ADMIN ==="
    )
    print()

    username = prompt_required(
        "Usuario administrador: "
    ).lower()

    full_name = prompt_required(
        "Nombre completo: "
    )

    email = prompt_required(
        "Correo electrónico: "
    ).lower()

    password = get_password()

    db = SessionLocal()

    try:
        existing = db.execute(
            select(User).where(
                or_(
                    User.username == username,
                    User.email == email,
                )
            )
        ).scalar_one_or_none()

        if existing:
            print()
            print(
                "ERROR: ya existe un usuario "
                "con ese username o correo."
            )
            sys.exit(1)

        admin_role = db.execute(
            select(Role).where(
                Role.code == "ADMIN"
            )
        ).scalar_one_or_none()

        if admin_role is None:
            print(
                "ERROR: el rol ADMIN no existe."
            )
            sys.exit(1)

        now = datetime.now(timezone.utc)

        user = User(
            uuid=uuid.uuid4(),
            username=username,
            email=email,
            full_name=full_name,
            password_hash=hash_password(
                password
            ),
            is_active=True,
            must_change_password=True,
            failed_login_attempts=0,
            created_at=now,
            updated_at=now,
        )

        user.roles.append(admin_role)

        db.add(user)
        db.flush()

        write_audit_log(
            db=db,
            action="USER_CREATED",
            result="SUCCESS",
            user_id=user.id,
            username=user.username,
            resource_type="user",
            resource_id=str(user.uuid),
            details={
                "created_by": "bootstrap",
                "roles": ["ADMIN"],
                "must_change_password": True,
            },
        )

        db.commit()

        print()
        print(
            "Administrador creado correctamente."
        )
        print(
            f"Usuario: {user.username}"
        )
        print(
            "Rol: ADMIN"
        )
        print(
            "Cambio de contraseña requerido: Sí"
        )

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    main()
