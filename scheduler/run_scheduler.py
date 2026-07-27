import time
import subprocess
from datetime import datetime


INTERVALO = 3600  # 1 hora


while True:

    print(
        f"[{datetime.now()}] Ejecutando enriquecimiento"
    )

    subprocess.run(
        [
            "python",
            "/app/vt_enrichment.py"
        ]
    )


    print(
        "Esperando próxima ejecución..."
    )


    time.sleep(INTERVALO)
