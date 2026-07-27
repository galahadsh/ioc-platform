from fastapi import APIRouter
from sqlalchemy import text

from database import engine


router = APIRouter(prefix="/api/analysis", tags=["Analysis"])


@router.get("/history")
def analysis_history():
    query = """
    SELECT
        id,
        nombre_archivo,
        estado,
        fecha_inicio,
        fecha_fin,
        total_iocs,
        analizados,
        maliciosos,
        sospechosos,
        limpios,
        errores
    FROM analysis
    ORDER BY id DESC
    LIMIT 50;
    """

    with engine.connect() as conn:
        rows = conn.execute(text(query)).mappings().all()

    return [
        {
            "id": row["id"],
            "archivo": row["nombre_archivo"],
            "estado": row["estado"],
            "fecha_inicio": (
                row["fecha_inicio"].isoformat()
                if row["fecha_inicio"]
                else None
            ),
            "fecha_fin": (
                row["fecha_fin"].isoformat()
                if row["fecha_fin"]
                else None
            ),
            "total_iocs": row["total_iocs"],
            "analizados": row["analizados"],
            "maliciosos": row["maliciosos"],
            "sospechosos": row["sospechosos"],
            "limpios": row["limpios"],
            "errores": row["errores"],
        }
        for row in rows
    ]