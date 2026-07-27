import os
import time
import base64
import requests
import psycopg2

from dotenv import load_dotenv
from datetime import datetime


# =====================================================
# CONFIG
# =====================================================

load_dotenv()

VT_API_KEY = os.getenv("VT_API_KEY")

if not VT_API_KEY:
    raise Exception("Falta VT_API_KEY")


HEADERS = {
    "x-apikey": VT_API_KEY
}


WAIT_TIME = 16


DB = {
    "host": "postgres",
    "database": "cyberintel",
    "user": "cyberintel",
    "password": "SuperPassword123",
    "port": 5432
}


# =====================================================
# URL ID VIRUSTOTAL
# =====================================================

def url_id(url):

    encoded = base64.urlsafe_b64encode(
        url.encode()
    ).decode()

    return encoded.rstrip("=")



# =====================================================
# CONSULTA VT
# =====================================================

def consultar_vt(valor, tipo):


    if tipo == "ip":

        url = (
            f"https://www.virustotal.com/api/v3/ip_addresses/{valor}"
        )


    elif tipo == "domain":

        url = (
            f"https://www.virustotal.com/api/v3/domains/{valor}"
        )


    elif tipo in [
        "md5",
        "sha1",
        "sha256"
    ]:

        url = (
            f"https://www.virustotal.com/api/v3/files/{valor}"
        )


    elif tipo == "url":

        url = (
            "https://www.virustotal.com/api/v3/urls/"
            f"{url_id(valor)}"
        )


    else:

        return {}



    while True:

        try:

            r = requests.get(
                url,
                headers=HEADERS,
                timeout=30
            )


            if r.status_code == 200:

                return r.json()["data"]["attributes"]


            elif r.status_code == 404:

                return {}


            elif r.status_code == 429:

                print(
                    "Limite VT alcanzado, esperando 60 segundos..."
                )

                time.sleep(60)


            elif r.status_code == 401:

                raise Exception(
                    "API Key inválida"
                )


            else:

                print(
                    f"VT error {r.status_code}"
                )

                return {}



        except Exception as e:

            raise e




# =====================================================
# MAIN
# =====================================================


conn = psycopg2.connect(
    **DB
)

cursor = conn.cursor()



cursor.execute(
    """
    SELECT
        id,
        valor,
        tipo
    FROM iocs
    WHERE vt_estado='pendiente'
    """
)


iocs = cursor.fetchall()


print(
    f"IOCs pendientes: {len(iocs)}"
)



contador = 0



for ioc_id, valor, tipo in iocs:


    print(
        f"Consultando {valor} ({tipo})"
    )


    try:


        atributos = consultar_vt(
            valor,
            tipo
        )


        stats = atributos.get(
            "last_analysis_stats",
            {}
        )


        malicious = stats.get(
            "malicious",
            0
        )


        suspicious = stats.get(
            "suspicious",
            0
        )


        harmless = stats.get(
            "harmless",
            0
        )


        undetected = stats.get(
            "undetected",
            0
        )


        cursor.execute(
            """
            UPDATE iocs
            SET

            malicious=%s,
            suspicious=%s,
            harmless=%s,
            undetected=%s,

            country=%s,
            owner=%s,
            asn=%s,

            proveedor_reputacion='VirusTotal',

            vt_estado='analizado',
            vt_fecha=%s,
            vt_error=NULL

            WHERE id=%s

            """,
            (

                malicious,
                suspicious,
                harmless,
                undetected,

                atributos.get(
                    "country",
                    ""
                ),

                atributos.get(
                    "as_owner",
                    ""
                ),

                str(
                    atributos.get(
                        "asn",
                        ""
                    )
                ),

                datetime.now(),

                ioc_id
            )
        )


    except Exception as e:


        cursor.execute(
            """
            UPDATE iocs
            SET

            vt_estado='error',
            vt_fecha=%s,
            vt_error=%s

            WHERE id=%s

            """,
            (
                datetime.now(),
                str(e),
                ioc_id
            )
        )



    conn.commit()


    contador += 1


    if contador < len(iocs):

        time.sleep(
            WAIT_TIME
        )



cursor.close()
conn.close()



print("==============================")
print("Enriquecimiento terminado")
print("==============================")
