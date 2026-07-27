import csv
import io
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, File, HTTPException, UploadFile
from sqlalchemy import text

from config import UPLOAD_DIR
from database import engine
from utils.ioc import detectar_tipo


router = APIRouter(prefix="/api", tags=["Upload"])

ALLOWED_COLUMNS = ("ioc", "valor", "src_ip", "url", "domain", "hash")


def obtener_valor_ioc(row: dict) -> str | None:
    for columna in ALLOWED_COLUMNS:
        valor = row.get(columna)

        if valor and valor.strip():
            return valor.strip()

    return None


@router.post("/upload")
async def upload_ioc(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="El archivo no tiene nombre.",
        )

    if Path(file.filename).suffix.lower() != ".csv":
        raise HTTPException(
            status_code=400,
            detail="Solo se permiten archivos CSV.",
        )

    contenido = await file.read()

    try:
        texto_csv = contenido.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise HTTPException(
            status_code=400,
            detail="El archivo debe estar codificado en UTF-8.",
        ) from exc

    nombre_seguro = f"{uuid4().hex}_{Path(file.filename).name}"
    ruta = UPLOAD_DIR / nombre_seguro
    ruta.write_bytes(contenido)

    with engine.begin() as conn:
        result = conn.execute(
            text("""
                INSERT INTO analysis (
                    nombre_archivo,
                    estado,
                    total_iocs
                )
                VALUES (
                    :archivo,
                    'procesando',
                    0
                )
                RETURNING id;
            """),
            {"archivo": file.filename},
        )

        analysis_id = result.scalar_one()

    reader = csv.DictReader(io.StringIO(texto_csv))

    if not reader.fieldnames:
        raise HTTPException(
            status_code=400,
            detail="El CSV no contiene encabezados.",
        )

    total_procesados = 0

    with engine.begin() as conn:
        for row in reader:
            valor = obtener_valor_ioc(row)

            if not valor:
                continue

            conn.execute(
                text("""
                    INSERT INTO iocs (
                        tipo,
                        valor,
                        fuente,
                        proveedor_reputacion,
                        vt_estado,
                        analysis_id
                    )
                    VALUES (
                        :tipo,
                        :valor,
                        :fuente,
                        'Pendiente',
                        'pendiente',
                        :analysis_id
                    )
                    ON CONFLICT (valor)
                    DO UPDATE SET
                        analysis_id = EXCLUDED.analysis_id,
                        fuente = EXCLUDED.fuente;
                """),
                {
                    "tipo": detectar_tipo(valor),
                    "valor": valor,
                    "fuente": file.filename,
                    "analysis_id": analysis_id,
                },
            )

            total_procesados += 1

        conn.execute(
            text("""
                UPDATE analysis
                SET
                    estado = 'finalizado',
                    total_iocs = (
                        SELECT COUNT(*)
                        FROM iocs
                        WHERE analysis_id = :analysis_id
                    ),
                    analizados = (
                        SELECT COUNT(*)
                        FROM iocs
                        WHERE analysis_id = :analysis_id
                        AND vt_estado = 'analizado'
                    ),
                    maliciosos = (
                        SELECT COUNT(*)
                        FROM iocs
                        WHERE analysis_id = :analysis_id
                        AND COALESCE(vt_malicious, 0) > 0
                    ),
                    sospechosos = 0,
                    limpios = (
                        SELECT COUNT(*)
                        FROM iocs
                        WHERE analysis_id = :analysis_id
                        AND vt_estado = 'analizado'
                        AND COALESCE(vt_malicious, 0) = 0
                    ),
                    fecha_fin = CURRENT_TIMESTAMP
                WHERE id = :analysis_id;
            """),
            {"analysis_id": analysis_id},
        )

    return {
        "status": "ok",
        "analysis_id": analysis_id,
        "iocs_procesados": total_procesados,
    }