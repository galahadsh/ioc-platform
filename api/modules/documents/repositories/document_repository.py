from __future__ import annotations

import uuid as uuid_lib
from datetime import datetime

from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session, selectinload

from modules.documents.models.document import Document
from modules.documents.models.document_status import (
    DocumentStatus,
)


class DocumentRepository:
    def __init__(
        self,
        db: Session,
    ) -> None:
        self.db = db

    def get_status_by_code(
        self,
        code: str,
    ) -> DocumentStatus | None:
        statement = select(
            DocumentStatus
        ).where(
            func.upper(
                DocumentStatus.code
            )
            == code.strip().upper()
        )

        return self.db.scalar(
            statement
        )

    def get_by_id(
        self,
        document_id: int,
    ) -> Document | None:
        statement = (
            select(Document)
            .options(
                selectinload(
                    Document.status
                )
            )
            .where(
                Document.id
                == document_id
            )
        )

        return self.db.scalar(
            statement
        )

    def get_by_uuid(
        self,
        document_uuid: uuid_lib.UUID,
    ) -> Document | None:
        statement = (
            select(Document)
            .options(
                selectinload(
                    Document.status
                )
            )
            .where(
                Document.uuid
                == document_uuid
            )
        )

        return self.db.scalar(
            statement
        )

    def get_by_sha256(
        self,
        sha256: str,
    ) -> Document | None:
        statement = (
            select(Document)
            .options(
                selectinload(
                    Document.status
                )
            )
            .where(
                Document.sha256
                == sha256.lower()
            )
            .order_by(
                desc(
                    Document.uploaded_at
                )
            )
            .limit(1)
        )

        return self.db.scalar(
            statement
        )

    def create(
        self,
        *,
        original_name: str,
        stored_name: str,
        bucket: str,
        object_name: str,
        size_bytes: int,
        sha256: str,
        md5: str,
        status_code: str = "UPLOADED",
        content_type: str | None = None,
        extension: str | None = None,
        source: str | None = None,
        tlp: str | None = None,
        classification: str | None = None,
        uploaded_by: str | None = None,
        document_uuid: (
            uuid_lib.UUID | None
        ) = None,
    ) -> Document:
        status = (
            self.get_status_by_code(
                status_code
            )
        )

        if status is None:
            raise ValueError(
                "Estado de documento "
                f"desconocido: {status_code}"
            )

        document = Document(
            uuid=(
                document_uuid
                or uuid_lib.uuid4()
            ),
            original_name=original_name,
            stored_name=stored_name,
            bucket=bucket,
            object_name=object_name,
            content_type=content_type,
            extension=extension,
            size_bytes=size_bytes,
            sha256=sha256.lower(),
            md5=md5.lower(),
            source=source,
            tlp=tlp,
            classification=classification,
            status_id=status.id,
            uploaded_by=uploaded_by,
        )

        self.db.add(
            document
        )

        self.db.flush()

        self.db.refresh(
            document
        )

        return document

    def change_status(
        self,
        document: Document,
        status_code: str,
        *,
        error_message: str | None = None,
    ) -> Document:
        status = (
            self.get_status_by_code(
                status_code
            )
        )

        if status is None:
            raise ValueError(
                "Estado de documento "
                f"desconocido: {status_code}"
            )

        document.status_id = status.id
        document.error_message = (
            error_message
        )
        document.updated_at = (
            datetime.utcnow()
        )

        if (
            status.code
            in {
                "PROCESSED",
                "CORRELATED",
            }
        ):
            document.processed_at = (
                datetime.utcnow()
            )

        self.db.flush()

        return document

    def list_paginated(
        self,
        *,
        page: int = 1,
        page_size: int = 25,
        search: str | None = None,
        status: str | None = None,
        source: str | None = None,
    ) -> tuple[
        list[Document],
        int,
    ]:
        conditions = []

        if search and search.strip():
            value = (
                f"%{search.strip()}%"
            )

            conditions.append(
                Document.original_name.ilike(
                    value
                )
            )

        if source and source.strip():
            conditions.append(
                Document.source.ilike(
                    f"%{source.strip()}%"
                )
            )

        if status and status.strip():
            conditions.append(
                Document.status.has(
                    DocumentStatus.code
                    == status
                    .strip()
                    .upper()
                )
            )

        count_statement = select(
            func.count(
                Document.id
            )
        )

        data_statement = (
            select(Document)
            .options(
                selectinload(
                    Document.status
                )
            )
        )

        if conditions:
            count_statement = (
                count_statement.where(
                    *conditions
                )
            )

            data_statement = (
                data_statement.where(
                    *conditions
                )
            )

        total = (
            self.db.scalar(
                count_statement
            )
            or 0
        )

        offset = (
            page - 1
        ) * page_size

        data_statement = (
            data_statement
            .order_by(
                desc(
                    Document.uploaded_at
                ),
                desc(
                    Document.id
                ),
            )
            .limit(
                page_size
            )
            .offset(
                offset
            )
        )

        documents = list(
            self.db.scalars(
                data_statement
            ).all()
        )

        return (
            documents,
            total,
        )

    def delete(
        self,
        document: Document,
    ) -> None:
        self.db.delete(
            document
        )

        self.db.flush()
