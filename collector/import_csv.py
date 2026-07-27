import pandas as pd
import psycopg2
import re
import os
from datetime import datetime


# =====================================================
# CONFIGURACION
# =====================================================

CSV_FILE = "/data/iocs.csv"


DB_CONFIG = {
    "host": "postgres",
    "database": "cyberintel",
    "user": "cyberintel",
    "password": "SuperPassword123",
    "port": 5432
}


# =====================================================
# DETECTAR TIPO IOC
# =====================================================

def detectar_tipo(ioc):

    ioc = str(ioc).strip()


    # IP
    ip_regex = r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$"

    if re.match(ip_regex, ioc):
        return "ip"


    # URL
    if ioc.startswith("http://") or ioc.startswith("https://"):
        return "url"


    # MD5
    if re.fullmatch(r"[a-fA-F0-9]{32}", ioc):
        return "md5"


    # SHA1
    if re.fullmatch(r"[a-fA-F0-9]{40}", ioc):
        return "sha1"


    # SHA256
    if re.fullmatch(r"[a-fA-F0-9]{64}", ioc):
        return "sha256"


    # Default
    return "domain"



# =====================================================
# CARGAR CSV
# =====================================================

if not os.path.exists(CSV_FILE):

    raise Exception(
        f"No existe el archivo {CSV_FILE}"
    )


df = pd.read_csv(CSV_FILE)


print("Columnas encontradas:")
print(df.columns.tolist())



# =====================================================
# NORMALIZAR FORMATOS
# =====================================================


# Caso antiguo:
# ioc

if "ioc" in df.columns:

    df["valor"] = df["ioc"]

    if "fuente" not in df.columns:
        df["fuente"] = "manual"


    df["tipo"] = df["valor"].apply(
        detectar_tipo
    )


# Caso nuevo:
# tipo,valor,fuente

elif "valor" in df.columns:


    if "tipo" not in df.columns:

        df["tipo"] = df["valor"].apply(
            detectar_tipo
        )


    if "fuente" not in df.columns:

        df["fuente"] = "manual"



else:

    raise Exception(
        "El CSV debe tener una columna 'ioc' o 'valor'"
    )



# Limpiar datos

df = df.dropna(
    subset=["valor"]
)


df["valor"] = (
    df["valor"]
    .astype(str)
    .str.strip()
)


df = df.drop_duplicates(
    subset=["valor"]
)



print(
    f"IOC encontrados: {len(df)}"
)



# =====================================================
# INSERTAR EN POSTGRESQL
# =====================================================


conn = psycopg2.connect(
    **DB_CONFIG
)


cursor = conn.cursor()



insertados = 0
existentes = 0



for _, row in df.iterrows():


    try:

        cursor.execute(
            """
            INSERT INTO iocs
            (
                tipo,
                valor,
                fuente,
                estado,
                fecha_creacion
            )
            VALUES
            (
                %s,
                %s,
                %s,
                'activo',
                %s
            )
            ON CONFLICT (valor)
            DO NOTHING
            """,
            (
                row["tipo"],
                row["valor"],
                row["fuente"],
                datetime.now()
            )
        )


        if cursor.rowcount == 1:

            insertados += 1

        else:

            existentes += 1



    except Exception as e:

        print(
            f"Error con IOC {row['valor']}: {e}"
        )



conn.commit()

cursor.close()
conn.close()



print("==============================")
print("Carga terminada")
print("==============================")
print(f"Nuevos IOC: {insertados}")
print(f"Ya existentes: {existentes}")
print("==============================")
