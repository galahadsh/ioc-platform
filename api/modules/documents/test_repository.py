import hashlib
import uuid

from database import SessionLocal
from modules.documents.repositories.document_repository import (
    DocumentRepository,
)


def main():
    db = SessionLocal()

    try:
        repository = (
            DocumentRepository(db)
        )

        payload = (
            b"Cyber Intelligence Platform "
            b"Document Repository Test"
        )

        sha256 = hashlib.sha256(
            payload
        ).hexdigest()

        md5 = hashlib.md5(
            payload
        ).hexdigest()

        uid = uuid.uuid4()

        document = repository.create(
            document_uuid=uid,
            original_name=(
                "repository-test.txt"
            ),
            stored_name=(
                f"{uid}.txt"
            ),
            bucket=(
                "cyber-intelligence-documents"
            ),
            object_name=(
                f"tests/{uid}.txt"
            ),
            content_type="text/plain",
            extension="txt",
            size_bytes=len(payload),
            sha256=sha256,
            md5=md5,
            source="INTERNAL",
            tlp="TLP:CLEAR",
            classification="TEST",
            status_code="UPLOADED",
            uploaded_by="system-test",
        )

        db.commit()

        document_id = (
            document.id
        )

        print(
            "Documento creado:",
            document_id,
        )

        loaded = (
            repository.get_by_id(
                document_id
            )
        )

        if loaded is None:
            raise RuntimeError(
                "No se encontró "
                "el documento."
            )

        print(
            "UUID:",
            loaded.uuid,
        )

        print(
            "Nombre:",
            loaded.original_name,
        )

        print(
            "SHA256:",
            loaded.sha256,
        )

        print(
            "Estado:",
            loaded.status.code,
        )

        print(
            "Bucket:",
            loaded.bucket,
        )

        print(
            "Object:",
            loaded.object_name,
        )

        repository.change_status(
            loaded,
            "PROCESSING",
        )

        db.commit()

        loaded = (
            repository.get_by_id(
                document_id
            )
        )

        print(
            "Nuevo estado:",
            loaded.status.code,
        )

        print()
        print(
            "DocumentRepository OK"
        )

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    main()
