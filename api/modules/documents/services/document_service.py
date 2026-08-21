from __future__ import annotations

import hashlib
import uuid
from pathlib import Path

from sqlalchemy.orm import Session

from modules.documents.queue import (
    DocumentQueue,
)
from modules.documents.repositories.document_repository import (
    DocumentRepository,
)
from modules.documents.storage.storage_service import (
    StorageService,
)


class DocumentService:
    def __init__(
        self,
        db: Session,
    ) -> None:
        self.db = db

        self.repository = (
            DocumentRepository(
                db
            )
        )

        self.storage = (
            StorageService()
        )

        self.queue = (
            DocumentQueue()
        )

    def create_document(
        self,
        *,
        filename: str,
        data: bytes,
        content_type: str | None = None,
        source: str | None = None,
        tlp: str | None = None,
        classification: str | None = None,
        uploaded_by: str | None = None,
    ):
        if not filename:
            raise ValueError(
                "El nombre del archivo "
                "es obligatorio."
            )

        if not data:
            raise ValueError(
                "El archivo está vacío."
            )

        document_uuid = (
            uuid.uuid4()
        )

        extension = (
            Path(filename)
            .suffix
            .lower()
            .lstrip(".")
        )

        sha256 = hashlib.sha256(
            data
        ).hexdigest()

        md5 = hashlib.md5(
            data
        ).hexdigest()

        stored_name = str(
            document_uuid
        )

        if extension:
            stored_name += (
                f".{extension}"
            )

        object_name = (
            f"documents/"
            f"{document_uuid}/"
            f"{stored_name}"
        )

        uploaded = False
        document = None

        try:
            storage_result = (
                self.storage.upload_bytes(
                    object_name=object_name,
                    data=data,
                    content_type=(
                        content_type
                        or
                        "application/octet-stream"
                    ),
                )
            )

            uploaded = True

            document = (
                self.repository.create(
                    document_uuid=(
                        document_uuid
                    ),
                    original_name=filename,
                    stored_name=(
                        stored_name
                    ),
                    bucket=(
                        storage_result[
                            "bucket"
                        ]
                    ),
                    object_name=(
                        storage_result[
                            "object_name"
                        ]
                    ),
                    content_type=(
                        content_type
                    ),
                    extension=(
                        extension
                        or None
                    ),
                    size_bytes=len(
                        data
                    ),
                    sha256=sha256,
                    md5=md5,
                    source=source,
                    tlp=tlp,
                    classification=(
                        classification
                    ),
                    uploaded_by=(
                        uploaded_by
                    ),
                    status_code=(
                        "UPLOADED"
                    ),
                )
            )

            self.db.commit()

            document = (
                self.repository.get_by_id(
                    document.id
                )
            )

            self.queue.enqueue(
                document.id
            )

            self.repository.change_status(
                document,
                "QUEUED",
            )

            self.db.commit()

            self.db.expire_all()

            return (
                self.repository.get_by_id(
                    document.id
                )
            )

        except Exception:
            self.db.rollback()

            if (
                uploaded
                and document is None
            ):
                try:
                    self.storage.delete(
                        object_name
                    )
                except Exception:
                    pass

            raise
