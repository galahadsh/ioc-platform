import os
import time
import requests
import psycopg2
from datetime import datetime


VT_API_KEY = os.getenv("VT_API_KEY")


DB = {
    "host": "postgres",
    "database": "cyberintel",
    "user": "cyberintel",
    "password": "SuperPassword123",
    "port": 5432
}


HEADERS = {
    "x-apikey": VT_API_KEY
}


VT_URL = "https://www.virustotal.com/api/v3"


def db_connect():
    return psycopg2.connect(**DB)



def vt_lookup(tipo, valor):

    try:

        if tipo == "ip":
            url = f"{VT_URL}/ip_addresses/{valor}"

        elif tipo == "domain":
            url = f"{VT_URL}/domains/{valor}"

        elif tipo in ["md5", "sha1", "sha256"]:
            url = f"{VT_URL}/files/{valor}"

        else:
            return None


        r = requests.get(
            url,
            headers=HEADERS,
            timeout=30
        )


        if r.status_code != 200:
            print(
                "VT error:",
                valor,
                r.status_code
            )
            return None


        attr = r.json()["data"]["attributes"]


        stats = attr.get(
            "last_analysis_stats",
            {}
        )


        return {

            "vt_malicious": stats.get("malicious", 0),
            "vt_suspicious": stats.get("suspicious", 0),
            "vt_harmless": stats.get("harmless", 0),
            "vt_undetected": stats.get("undetected", 0)

        }


    except Exception as e:

        print(
            "VT Exception:",
            e
        )

        return None




def actualizar_analysis(conn, analysis_id):

    cur = conn.cursor()


    cur.execute(
    """

    UPDATE analysis

    SET

    estado='finalizado',

    total_iocs =
    (
        SELECT COUNT(*)
        FROM iocs
        WHERE analysis_id=%s
    ),


    analizados =
    (
        SELECT COUNT(*)
        FROM iocs
        WHERE analysis_id=%s
        AND vt_estado='analizado'
    ),


    maliciosos =
    (
        SELECT COUNT(*)
        FROM iocs
        WHERE analysis_id=%s
        AND vt_malicious > 0
    ),


    sospechosos =
    (
        SELECT COUNT(*)
        FROM iocs
        WHERE analysis_id=%s
        AND vt_suspicious > 0
        AND vt_malicious = 0
    ),


    limpios =
    (
        SELECT COUNT(*)
        FROM iocs
        WHERE analysis_id=%s
        AND vt_malicious = 0
        AND vt_suspicious = 0
    ),


    fecha_fin=CURRENT_TIMESTAMP


    WHERE id=%s

    """,
    (
        analysis_id,
        analysis_id,
        analysis_id,
        analysis_id,
        analysis_id,
        analysis_id
    ))


    cur.close()




def process():

    conn = db_connect()

    cur = conn.cursor()


    cur.execute(
    """

    SELECT

    id,
    analysis_id,
    tipo,
    valor

    FROM iocs

    WHERE vt_estado='pendiente'

    LIMIT 10

    """
    )


    rows = cur.fetchall()


    print(
        "Pendientes:",
        len(rows)
    )


    analyses = set()



    for ioc_id, analysis_id, tipo, valor in rows:


        print(
            "Consultando:",
            valor
        )


        result = vt_lookup(
            tipo,
            valor
        )


        if result:


            cur.execute(
            """

            UPDATE iocs

            SET

            vt_malicious=%s,
            vt_suspicious=%s,
            vt_harmless=%s,
            vt_undetected=%s,

            proveedor_reputacion='VirusTotal',

            vt_estado='analizado',

            ultima_consulta=%s


            WHERE id=%s


            """,
            (

                result["vt_malicious"],
                result["vt_suspicious"],
                result["vt_harmless"],
                result["vt_undetected"],
                datetime.now(),
                ioc_id

            ))


            analyses.add(
                analysis_id
            )


        else:


            cur.execute(
            """

            UPDATE iocs

            SET

            vt_estado='error'


            WHERE id=%s


            """,
            (
                ioc_id,
            ))



    for analysis_id in analyses:

        actualizar_analysis(
            conn,
            analysis_id
        )


    conn.commit()


    cur.close()

    conn.close()




print(
    "IOC Collector iniciado"
)



while True:

    try:

        process()


    except Exception as e:

        print(
            "ERROR:",
            e
        )


    time.sleep(300)

