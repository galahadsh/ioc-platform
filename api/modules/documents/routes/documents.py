import math
from io import BytesIO

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Query,
    UploadFile,
)
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from database import get_db

from modules.documents.repositories.document_repository import (
    DocumentRepository,
)
from modules.documents.schemas.document import (
    DocumentListResponse,
    DocumentResponse,
    DocumentUploadResponse,
)
from modules.documents.services.document_service import (
    DocumentService,
)
from modules.documents.storage.storage_service import (
    StorageService,
)


router = APIRouter(
    prefix="/api/v3/documents",
    tags=["Documents"],
)


def serialize_document(document) -> DocumentResponse:
    return DocumentResponse(
        id=document.id,
        uuid=document.uuid,
        original_name=document.original_name,
        content_type=document.content_type,
        extension=document.extension,
        size_bytes=document.size_bytes,
        sha256=document.sha256,
        md5=document.md5,
        source=document.source,
        tlp=document.tlp,
        classification=document.classification,
        status=document.status.code,
        uploaded_by=document.uploaded_by,
        uploaded_at=document.uploaded_at,
        processed_at=document.processed_at,
    )


@router.post(
    "",
    response_model=DocumentUploadResponse,
    status_code=202,
)
async def upload_document(
    file: UploadFile = File(...),
    source: str | None = Form(None),
    tlp: str | None = Form(None),
    classification: str | None = Form(None),
    uploaded_by: str | None = Form(None),
    db: Session = Depends(get_db),
):
    try:
        data = await file.read()

        if not data:
            raise HTTPException(
                status_code=400,
                detail="El archivo está vacío.",
            )

        service = DocumentService(db)

        document = service.create_document(
            filename=file.filename or "unnamed",
            data=data,
            content_type=file.content_type,
            source=source,
            tlp=tlp,
            classification=classification,
            uploaded_by=uploaded_by,
        )

        return DocumentUploadResponse(
            document=serialize_document(document),
            message=(
                "Documento aceptado "
                "para procesamiento."
            ),
        )

    except HTTPException:
        raise

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error),
        ) from error

    finally:
        await file.close()


@router.get(
    "",
    response_model=DocumentListResponse,
)
def list_documents(
    page: int = Query(
        1,
        ge=1,
    ),
    page_size: int = Query(
        25,
        ge=1,
        le=100,
    ),
    search: str | None = None,
    status: str | None = None,
    source: str | None = None,
    db: Session = Depends(get_db),
):
    repository = DocumentRepository(db)

    documents, total = repository.list_paginated(
        page=page,
        page_size=page_size,
        search=search,
        status=status,
        source=source,
    )

    pages = (
        math.ceil(total / page_size)
        if total
        else 0
    )

    return DocumentListResponse(
        items=[
            serialize_document(document)
            for document in documents
        ],
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )


@router.get(
    "/{document_id}",
    response_model=DocumentResponse,
)
def get_document(
    document_id: int,
    db: Session = Depends(get_db),
):
    repository = DocumentRepository(db)

    document = repository.get_by_id(
        document_id
    )

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Documento no encontrado.",
        )

    return serialize_document(
        document
    )


@router.get(
    "/{document_id}/download",
)
def download_document(
    document_id: int,
    db: Session = Depends(get_db),
):
    repository = DocumentRepository(db)

    document = repository.get_by_id(
        document_id
    )

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Documento no encontrado.",
        )

    storage = StorageService()

    try:
        data = storage.download_bytes(
            document.object_name
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=(
                "No fue posible recuperar "
                "el archivo."
            ),
        ) from error

    return StreamingResponse(
        BytesIO(data),
        media_type=(
            document.content_type
            or "application/octet-stream"
        ),
        headers={
            "Content-Disposition": (
                'attachment; filename="'
                f'{document.original_name}"'
            ),
        },
    )
