from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from sqlalchemy import create_engine, text
from fastapi.responses import JSONResponse


app = FastAPI(
    title="IOC Platform"
)


# ==============================
# DATABASE
# ==============================

DATABASE_URL = "postgresql://cyberintel:SuperPassword123@ioc-postgres:5432/cyberintel"

engine = create_engine(
    DATABASE_URL
)


# ==============================
# HEALTH
# ==============================

@app.get("/health")
def health():

    return {
        "status": "ok"
    }



# ==============================
# STATS
# ==============================

@app.get("/api/stats")
def stats():

    query = """
    SELECT
        COUNT(*) AS total,
        COUNT(*) FILTER (WHERE malicious > 0) AS maliciosos,
        COUNT(*) FILTER (WHERE suspicious > 0 AND malicious = 0) AS sospechosos,
        COUNT(*) FILTER (WHERE malicious = 0 AND suspicious = 0) AS limpios
    FROM iocs;
    """


    with engine.connect() as conn:

        row = conn.execute(
            text(query)
        ).fetchone()


    return {
        "total_iocs": row.total,
        "maliciosos": row.maliciosos,
        "sospechosos": row.sospechosos,
        "limpios": row.limpios
    }



# ==============================
# IOC MALICIOSOS
# ==============================

@app.get("/api/iocs/malicious")
def malicious_iocs():

    query = """
    SELECT

        valor,
        tipo,
        fuente,
        malicious,
        suspicious,
        harmless,
        undetected,
        country,
        owner,
        asn,
        vt_estado,
        vt_fecha

    FROM iocs

    WHERE malicious > 0

    ORDER BY malicious DESC;
    """


    data = []


    with engine.connect() as conn:

        result = conn.execute(
            text(query)
        )


        for row in result:

            item = dict(row._mapping)


            if item.get("vt_fecha"):

                item["vt_fecha"] = item["vt_fecha"].isoformat()


            data.append(item)



    return JSONResponse(
        content=data
    )



# ==============================
# TODOS LOS IOC
# ==============================

@app.get("/api/iocs")
def all_iocs():

    query = """
    SELECT

        valor,
        tipo,
        fuente,
        malicious,
        suspicious,
        harmless,
        undetected,
        country,
        owner,
        asn,
        vt_estado,
        vt_fecha

    FROM iocs

    ORDER BY id DESC;
    """


    data = []


    with engine.connect() as conn:

        result = conn.execute(
            text(query)
        )


        for row in result:

            item = dict(row._mapping)


            if item.get("vt_fecha"):

                item["vt_fecha"] = item["vt_fecha"].isoformat()


            data.append(item)



    return JSONResponse(
        content=data
    )



# ==============================
# FRONTEND
# ==============================

app.mount(
    "/",
    StaticFiles(
        directory="static",
        html=True
    ),
    name="static"
)
