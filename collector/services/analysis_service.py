from psycopg2.extensions import connection


def update_analysis(
    conn: connection,
    analysis_id: int,
) -> None:
    """
    Recalcula las estadísticas de un análisis.

    El análisis solo se marca como finalizado cuando ya no tiene
    IOC pendientes.
    """

    with conn.cursor() as cursor:
        cursor.execute(
            """
            UPDATE analysis
            SET
                estado = CASE
                    WHEN EXISTS (
                        SELECT 1
                        FROM iocs
                        WHERE analysis_id = %s
                          AND vt_estado = 'pendiente'
                    )
                    THEN 'procesando'
                    ELSE 'finalizado'
                END,

                total_iocs = (
                    SELECT COUNT(*)
                    FROM iocs
                    WHERE analysis_id = %s
                ),

                analizados = (
                    SELECT COUNT(*)
                    FROM iocs
                    WHERE analysis_id = %s
                      AND vt_estado = 'analizado'
                ),

                errores = (
                    SELECT COUNT(*)
                    FROM iocs
                    WHERE analysis_id = %s
                      AND vt_estado = 'error'
                ),

                maliciosos = (
                    SELECT COUNT(*)
                    FROM iocs
                    WHERE analysis_id = %s
                      AND vt_estado = 'analizado'
                      AND COALESCE(vt_malicious, 0) > 0
                ),

                sospechosos = (
                    SELECT COUNT(*)
                    FROM iocs
                    WHERE analysis_id = %s
                      AND vt_estado = 'analizado'
                      AND COALESCE(vt_malicious, 0) = 0
                      AND COALESCE(vt_suspicious, 0) > 0
                ),

                limpios = (
                    SELECT COUNT(*)
                    FROM iocs
                    WHERE analysis_id = %s
                      AND vt_estado = 'analizado'
                      AND COALESCE(vt_malicious, 0) = 0
                      AND COALESCE(vt_suspicious, 0) = 0
                ),

                fecha_fin = CASE
                    WHEN EXISTS (
                        SELECT 1
                        FROM iocs
                        WHERE analysis_id = %s
                          AND vt_estado = 'pendiente'
                    )
                    THEN NULL
                    ELSE CURRENT_TIMESTAMP
                END

            WHERE id = %s
            """,
            (
                analysis_id,
                analysis_id,
                analysis_id,
                analysis_id,
                analysis_id,
                analysis_id,
                analysis_id,
                analysis_id,
                analysis_id,
            ),
        )