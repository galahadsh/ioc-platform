from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import FileResponse


router = APIRouter(
    prefix="/api/templates",
    tags=["Templates"],
)


@router.get("/ioc-enterprise")
def download_ioc_enterprise_template():
    file_path = (
        Path(__file__).resolve().parent.parent
        / "static"
        / "templates"
        / "ioc_enterprise_template.csv"
    )

    return FileResponse(
        path=file_path,
        media_type="text/csv",
        filename="ioc_enterprise_template.csv",
    )
