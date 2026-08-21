from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from routes import ioc_details

from config import STATIC_DIR
from modules.dashboard import router as dashboard_v2_router
from modules.iocs import router as iocs_orm_router

from modules.documents.routes import (
    router as documents_router,
)
from routes import (
    analysis,
    enrichment,
    health,
    iocs,
    stats,
    templates,
    upload,
)


app = FastAPI(
    title="IOC Platform",
    description=(
        "Plataforma para gestión y enriquecimiento "
        "de indicadores de compromiso."
    ),
    version="1.0.0-alpha",
)


app.mount(
    "/static",
    StaticFiles(directory=str(STATIC_DIR)),
    name="static",
)


@app.get(
    "/",
    include_in_schema=False,
)
def home():
    return FileResponse(
        STATIC_DIR / "index.html"
    )


@app.get(
    "/enterprise",
    include_in_schema=False,
)
def enterprise_home():
    return FileResponse(
        STATIC_DIR / "enterprise" / "index.html"
    )


app.include_router(enrichment.router)
app.include_router(templates.router)
app.include_router(dashboard_v2_router)
app.include_router(health.router)
app.include_router(stats.router)
app.include_router(upload.router)
app.include_router(iocs.router)
app.include_router(analysis.router)
app.include_router(iocs_orm_router)
app.include_router(ioc_details.router)
app.include_router(documents_router)
