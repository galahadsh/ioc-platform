from argon2 import PasswordHasher
from argon2.exceptions import (
    InvalidHashError,
    VerificationError,
    VerifyMismatchError,
)


password_hasher = PasswordHasher()


def hash_password(password: str) -> str:
    """
    Genera un hash Argon2id de una contraseña.
    """
    return password_hasher.hash(password)


def verify_password(
    password: str,
    password_hash: str,
) -> bool:
    """
    Verifica una contraseña contra un hash Argon2id.
    """
    try:
        return password_hasher.verify(
            password_hash,
            password,
        )

    except (
        VerifyMismatchError,
        VerificationError,
        InvalidHashError,
    ):
        return False


def needs_rehash(password_hash: str) -> bool:
    """
    Permite actualizar hashes antiguos si en el futuro
    cambiamos los parámetros de Argon2.
    """
    try:
        return password_hasher.check_needs_rehash(
            password_hash
        )
    except InvalidHashError:
        return True
