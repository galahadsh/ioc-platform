from fastapi import APIRouter
from sqlalchemy import text

from database import engine


router = APIRouter(prefix="/api/iocs", tags=["IOCs"])


@router.get("/malicious")
def malicious_iocs():
    query = """
    SELECT
        id,
        tipo,
        valor,
        vt_malicious,
        vt_score,
        proveedor_reputacion,
        vt_estado,
        fuente,
        fecha_creacion
    FROM iocs
    WHERE COALESCE(vt_malicious, 0) > 0
    ORDER BY vt_malicious DESC, id DESC
    LIMIT 100;
    """

    with engine.connect() as conn:
        rows = conn.execute(text(query)).mappings().all()

    return [
        {
            "id": row["id"],
            "tipo": row["tipo"],
            "valor": row["valor"],
            "malicious": row["vt_malicious"],
            "vt_score": row["vt_score"],
            "proveedor": row["proveedor_reputacion"],
            "estado": row["vt_estado"],
            "fuente": row["fuente"],
            "fecha_creacion": (
                row["fecha_creacion"].isoformat()
                if row["fecha_creacion"]
                else None
            ),
        }
        for row in rows
    ]