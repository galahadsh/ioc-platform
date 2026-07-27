import psycopg2
import pandas as pd
from datetime import datetime


conn = psycopg2.connect(
    host="postgres",
    database="cyberintel",
    user="cyberintel",
    password="SuperPassword123",
    port=5432
)


query = """
SELECT
    valor,
    tipo,
    fuente,
    malicious,
    suspicious,
    harmless,
    pais,
    asn,
    proveedor_reputacion,
    ultima_consulta
FROM iocs;
"""


df = pd.read_sql(
    query,
    conn
)


conn.close()


total = len(df)


maliciosos = df[
    (df["malicious"] > 0) |
    (df["suspicious"] > 0)
]


limpios = df[
    (df["malicious"] == 0) &
    (df["suspicious"] == 0)
]


fecha = datetime.now().strftime(
    "%Y%m%d_%H%M"
)


archivo = (
    f"/exports/"
    f"IOC_Report_{fecha}.xlsx"
)


with pd.ExcelWriter(archivo) as writer:

    resumen = pd.DataFrame(
        {
            "Metrica":[
                "Total IOC analizados",
                "IOC maliciosos",
                "IOC limpios"
            ],
            "Cantidad":[
                total,
                len(maliciosos),
                len(limpios)
            ]
        }
    )


    resumen.to_excel(
        writer,
        sheet_name="Resumen",
        index=False
    )


    maliciosos.to_excel(
        writer,
        sheet_name="Maliciosos",
        index=False
    )


    df.to_excel(
        writer,
        sheet_name="Todos",
        index=False
    )


print("==============================")
print("Reporte generado")
print("==============================")
print(f"Total analizados: {total}")
print(f"Maliciosos: {len(maliciosos)}")
print(f"Limpios: {len(limpios)}")
print(f"Archivo: {archivo}")
