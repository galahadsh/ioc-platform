from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from routes.iocs_orm import router as iocs_orm_router
from routes.dashboard_v2 import router as dashboard_v2_router
from config import STATIC_DIR
from routes import analysis, health, iocs, stats, upload


app = FastAPI(
    title="IOC Platform",
    description="Plataforma para gestión y enriquecimiento de indicadores de compromiso.",
    version="1.0.0-alpha",
)

app.mount(
    "/static",
    StaticFiles(directory=str(STATIC_DIR)),
    name="static",
)


@app.get("/", include_in_schema=False)
def home():
    return FileResponse(STATIC_DIR / "index.html")


app.include_router(dashboard_v2_router)
app.include_router(health.router)
app.include_router(stats.router)
app.include_router(upload.router)
app.include_router(iocs.router)
app.include_router(analysis.router)
app.include_router(iocs_orm_router)
