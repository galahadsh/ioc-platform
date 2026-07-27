import csv
import io
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from sqlalchemy import text

from config import UPLOAD_DIR
from database import engine
from utils.ioc import detectar_tipo


router = APIRouter(prefix="/api", tags=["Upload"])

ALLOWED_COLUMNS = (
    "ioc",
    "valor",
    "src_ip",
    "url",
    "domain",
    "hash",
)


def limpiar_texto(valor: str | None) -> str | None:
    """
    Limpia campos opcionales recibidos desde el formulario o CSV.
    Convierte cadenas vacías en None.
    """
    if valor is None:
        return None

    valor_limpio = valor.strip()

    return valor_limpio or None


def obtener_valor_ioc(row: dict) -> str | None:
    """
    Obtiene el IOC desde cualquiera de las columnas permitidas.
    """
    for columna in ALLOWED_COLUMNS:
        valor = row.get(columna)

        if valor and valor.strip():
            return valor.strip()

    return None


def obtener_campo_csv(
    row: dict,
    nombres_posibles: tuple[str, ...],
) -> str | None:
    """
    Busca un campo opcional dentro del CSV usando distintos nombres posibles.
    """
    for nombre in nombres_posibles:
        valor = row.get(nombre)

        if valor and valor.strip():
            return valor.strip()

    return None


@router.post("/upload")
async def upload_ioc(
    file: UploadFile = File(...),
    campaign: str | None = Form(default=None),
    malware_family: str | None = Form(default=None),
):
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

    campaign_form = limpiar_texto(campaign)
    malware_family_form = limpiar_texto(malware_family)

    contenido = await file.read()

    if not contenido:
        raise HTTPException(
            status_code=400,
            detail="El archivo CSV está vacío.",
        )

    try:
        texto_csv = contenido.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise HTTPException(
            status_code=400,
            detail="El archivo debe estar codificado en UTF-8.",
        ) from exc

    reader = csv.DictReader(io.StringIO(texto_csv))

    if not reader.fieldnames:
        raise HTTPException(
            status_code=400,
            detail="El CSV no contiene encabezados.",
        )

    # Normaliza encabezados del CSV:
    # " Valor " -> "valor"
    reader.fieldnames = [
        encabezado.strip().lower()
        if encabezado
        else encabezado
        for encabezado in reader.fieldnames
    ]

    columnas_disponibles = {
        columna
        for columna in reader.fieldnames
        if columna
    }

    if not columnas_disponibles.intersection(ALLOWED_COLUMNS):
        raise HTTPException(
            status_code=400,
            detail=(
                "El CSV debe contener al menos una columna de IOC: "
                "ioc, valor, src_ip, url, domain o hash."
            ),
        )

    UPLOAD_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    nombre_seguro = (
        f"{uuid4().hex}_{Path(file.filename).name}"
    )

    ruta = UPLOAD_DIR / nombre_seguro
    ruta.write_bytes(contenido)

    total_procesados = 0
    total_nuevos = 0
    total_actualizados = 0
    total_omitidos = 0

    try:
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
                {
                    "archivo": file.filename,
                },
            )

            analysis_id = result.scalar_one()

            for row in reader:
                # Normaliza las claves de cada fila.
                row_normalizada = {
                    str(clave).strip().lower(): valor
                    for clave, valor in row.items()
                    if clave is not None
                }

                valor = obtener_valor_ioc(row_normalizada)

                if not valor:
                    total_omitidos += 1
                    continue

                campaign_csv = obtener_campo_csv(
                    row_normalizada,
                    (
                        "campaign",
                        "campana",
                        "campaña",
                    ),
                )

                malware_family_csv = obtener_campo_csv(
                    row_normalizada,
                    (
                        "malware_family",
                        "malware",
                        "familia_malware",
                        "familia_de_malware",
                    ),
                )

                # El valor del CSV tiene prioridad.
                # Si no existe, se usa el valor enviado desde el formulario.
                campaign_final = (
                    campaign_csv
                    or campaign_form
                )

                malware_family_final = (
                    malware_family_csv
                    or malware_family_form
                )

                insert_result = conn.execute(
                    text("""
                        INSERT INTO iocs (
                            tipo,
                            valor,
                            fuente,
                            proveedor_reputacion,
                            vt_estado,
                            analysis_id,
                            campaign,
                            malware_family
                        )
                        VALUES (
                            :tipo,
                            :valor,
                            :fuente,
                            'Pendiente',
                            'pendiente',
                            :analysis_id,
                            :campaign,
                            :malware_family
                        )
                        ON CONFLICT (valor)
                        DO UPDATE SET
                            tipo = EXCLUDED.tipo,
                            analysis_id = EXCLUDED.analysis_id,
                            fuente = EXCLUDED.fuente,
                            campaign = COALESCE(
                                EXCLUDED.campaign,
                                iocs.campaign
                            ),
                            malware_family = COALESCE(
                                EXCLUDED.malware_family,
                                iocs.malware_family
                            )
                        RETURNING
                            id,
                            (xmax = 0) AS insertado;
                    """),
                    {
                        "tipo": detectar_tipo(valor),
                        "valor": valor,
                        "fuente": file.filename,
                        "analysis_id": analysis_id,
                        "campaign": campaign_final,
                        "malware_family": malware_family_final,
                    },
                )

                resultado_ioc = insert_result.mappings().one()

                if resultado_ioc["insertado"]:
                    total_nuevos += 1
                else:
                    total_actualizados += 1

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
                              AND vt_estado = 'analizado'
                              AND COALESCE(vt_malicious, 0) > 0
                        ),

                        sospechosos = (
                            SELECT COUNT(*)
                            FROM iocs
                            WHERE analysis_id = :analysis_id
                              AND vt_estado = 'analizado'
                              AND COALESCE(vt_malicious, 0) = 0
                              AND COALESCE(vt_suspicious, 0) > 0
                        ),

                        limpios = (
                            SELECT COUNT(*)
                            FROM iocs
                            WHERE analysis_id = :analysis_id
                              AND vt_estado = 'analizado'
                              AND COALESCE(vt_malicious, 0) = 0
                              AND COALESCE(vt_suspicious, 0) = 0
                        ),

                        fecha_fin = CURRENT_TIMESTAMP

                    WHERE id = :analysis_id;
                """),
                {
                    "analysis_id": analysis_id,
                },
            )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Error al procesar el archivo: {exc}",
        ) from exc

    return {
        "status": "ok",
        "analysis_id": analysis_id,
        "archivo": file.filename,
        "campaign": campaign_form,
        "malware_family": malware_family_form,
        "iocs_procesados": total_procesados,
        "iocs_nuevos": total_nuevos,
        "iocs_actualizados": total_actualizados,
        "filas_omitidas": total_omitidos,
    }