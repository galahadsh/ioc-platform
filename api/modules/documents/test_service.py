from database import SessionLocal
from modules.documents.services.document_service import (
    DocumentService,
)


def main():
    db = SessionLocal()

    try:
        service = DocumentService(
            db
        )

        payload = (
            b"Cyber Intelligence Platform\n"
            b"Document Service Integration Test\n"
        )

        document = (
            service.create_document(
                filename=(
                    "intelligence-test.txt"
                ),
                data=payload,
                content_type="text/plain",
                source="INTERNAL",
                tlp="TLP:CLEAR",
                classification="TEST",
                uploaded_by="system-test",
            )
        )

        if document is None:
            raise RuntimeError(
                "DocumentService no devolvió "
                "el documento."
            )

        print()
        print(
            "DocumentService OK"
        )

        print(
            "ID:",
            document.id,
        )

        print(
            "UUID:",
            document.uuid,
        )

        print(
            "Nombre:",
            document.original_name,
        )

        print(
            "Estado:",
            document.status.code,
        )

        print(
            "SHA256:",
            document.sha256,
        )

        print(
            "MD5:",
            document.md5,
        )

        print(
            "Bucket:",
            document.bucket,
        )

        print(
            "Object:",
            document.object_name,
        )

        exists = (
            service.storage.exists(
                document.object_name
            )
        )

        print(
            "Existe en MinIO:",
            exists,
        )

        if not exists:
            raise RuntimeError(
                "El registro existe en "
                "PostgreSQL pero el objeto "
                "no existe en MinIO."
            )

        downloaded = (
            service.storage.download_bytes(
                document.object_name
            )
        )

        if downloaded != payload:
            raise RuntimeError(
                "El contenido descargado "
                "no coincide."
            )

        print(
            "Contenido validado: OK"
        )

        print()
        print(
            "MinIO -> PostgreSQL -> "
            "Readback: OK"
        )

    finally:
        db.close()


if __name__ == "__main__":
    main()
