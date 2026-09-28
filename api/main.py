from fastapi import Depends, FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from routes import ioc_details

from config import STATIC_DIR
from modules.dashboard import router as dashboard_v2_router
from modules.iocs import router as iocs_orm_router
from modules.auth import router as auth_router
from modules.auth.dependencies import require_password_changed
from modules.auth.routes.admin_users import router as admin_users_router

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


app.include_router(
    enrichment.router,
    dependencies=[
        Depends(require_password_changed),
    ],
)
app.include_router(
    templates.router,
    dependencies=[
        Depends(require_password_changed),
    ],
)
app.include_router(
    dashboard_v2_router,
    dependencies=[
        Depends(require_password_changed),
    ],
)
app.include_router(health.router)
app.include_router(
    stats.router,
    dependencies=[
        Depends(require_password_changed),
    ],
)
app.include_router(
    upload.router,
    dependencies=[
        Depends(require_password_changed),
    ],
)
app.include_router(
    iocs.router,
    dependencies=[
        Depends(require_password_changed),
    ],
)
app.include_router(
    analysis.router,
    dependencies=[
        Depends(require_password_changed),
    ],
)
app.include_router(
    iocs_orm_router,
    dependencies=[
        Depends(require_password_changed),
    ],
)
app.include_router(
    ioc_details.router,
    dependencies=[
        Depends(require_password_changed),
    ],
)
app.include_router(
    documents_router,
    dependencies=[
        Depends(require_password_changed),
    ],
)
app.include_router(auth_router)
app.include_router(admin_users_router)
