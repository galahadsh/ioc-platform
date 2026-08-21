import os
import sys
import time

sys.path.insert(
    0,
    "/app",
)

from database import SessionLocal

from modules.documents.queue import (
    DocumentQueue,
)
from modules.documents.repositories.document_repository import (
    DocumentRepository,
)


def process_document(
    document_id: int,
) -> None:
    db = SessionLocal()

    try:
        repository = (
            DocumentRepository(
                db
            )
        )

        document = (
            repository.get_by_id(
                document_id
            )
        )

        if document is None:
            print(
                f"[WARN] Documento "
                f"{document_id} no existe."
            )
            return

        repository.change_status(
            document,
            "PROCESSING",
        )

        db.commit()

        print(
            f"[PROCESSING] "
            f"document_id={document_id}"
        )

        # Procesamiento mínimo.
        # Después agregaremos:
        # OCR
        # IOC extraction
        # enrichment
        # correlation

        time.sleep(2)

        repository.change_status(
            document,
            "PROCESSED",
        )

        db.commit()

        print(
            f"[PROCESSED] "
            f"document_id={document_id}"
        )

    except Exception as error:
        db.rollback()

        try:
            repository = (
                DocumentRepository(
                    db
                )
            )

            document = (
                repository.get_by_id(
                    document_id
                )
            )

            if document is not None:
                repository.change_status(
                    document,
                    "ERROR",
                    error_message=str(
                        error
                    ),
                )

                db.commit()

        except Exception:
            db.rollback()

        print(
            "[ERROR] "
            f"document_id="
            f"{document_id}: "
            f"{error}"
        )

    finally:
        db.close()


def main() -> None:
    queue = DocumentQueue()

    print(
        "Document Worker iniciado.",
        flush=True,
    )

    print(
        "Queue:",
        queue.queue_name,
        flush=True,
    )

    while True:
        try:
            message = queue.dequeue(
                timeout=5
            )

            if message is None:
                continue

            document_id = int(
                message[
                    "document_id"
                ]
            )

            process_document(
                document_id
            )

        except Exception as error:
            print(
                "[QUEUE ERROR] "
                f"{error}",
                flush=True,
            )

            time.sleep(5)


if __name__ == "__main__":
    main()
