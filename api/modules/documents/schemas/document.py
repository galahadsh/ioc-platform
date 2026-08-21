from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class DocumentResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int
    uuid: UUID
    original_name: str
    content_type: str | None = None
    extension: str | None = None
    size_bytes: int
    sha256: str
    md5: str
    source: str | None = None
    tlp: str | None = None
    classification: str | None = None
    status: str
    uploaded_by: str | None = None
    uploaded_at: datetime
    processed_at: datetime | None = None


class DocumentUploadResponse(BaseModel):
    document: DocumentResponse
    message: str


class DocumentListResponse(BaseModel):
    items: list[DocumentResponse]
    total: int
    page: int
    page_size: int
    pages: int
