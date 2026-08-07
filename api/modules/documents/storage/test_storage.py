import hashlib
import uuid

from modules.documents.storage.storage_service import (
    StorageService,
)


def main() -> None:
    storage = StorageService()

    payload = (
        b"Cyber Intelligence Platform "
        b"Storage Test"
    )

    object_name = (
        "tests/"
        f"{uuid.uuid4()}.txt"
    )

    expected_hash = hashlib.sha256(
        payload
    ).hexdigest()

    print(
        "Objeto:",
        object_name,
    )

    print(
        "SHA256 esperado:",
        expected_hash,
    )

    upload = storage.upload_bytes(
        object_name=object_name,
        data=payload,
        content_type="text/plain",
    )

    print(
        "Upload OK:",
        upload,
    )

    if not storage.exists(
        object_name
    ):
        raise RuntimeError(
            "El objeto no existe "
            "después del upload."
        )

    downloaded = (
        storage.download_bytes(
            object_name
        )
    )

    downloaded_hash = hashlib.sha256(
        downloaded
    ).hexdigest()

    print(
        "SHA256 descargado:",
        downloaded_hash,
    )

    if (
        downloaded_hash
        != expected_hash
    ):
        raise RuntimeError(
            "El archivo descargado "
            "no coincide con el original."
        )

    storage.delete(
        object_name
    )

    if storage.exists(
        object_name
    ):
        raise RuntimeError(
            "El objeto no fue eliminado."
        )

    print()
    print(
        "StorageService OK"
    )
    print(
        "Upload -> Download -> "
        "Hash -> Delete: OK"
    )


if __name__ == "__main__":
    main()
