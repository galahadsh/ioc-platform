import { uploadIOC } from "./api.js";
import { cargarDashboard } from "./dashboard.js";
import { cargarHistorial } from "./history.js";

export async function subirArchivo() {

    const archivo = document.getElementById("archivo").files[0];

    if (!archivo) {
        alert("Selecciona un archivo CSV");
        return;
    }

    const form = new FormData();
    form.append("file", archivo);

    try {

        const resultado = await uploadIOC(form);

        document.getElementById("resultado").innerHTML =
            `Carga completada - Analysis ID: ${resultado.analysis_id} | IOC cargados: ${resultado.iocs_cargados}`;

        await cargarDashboard();
        await cargarHistorial();

    } catch (error) {

        console.error(error);

        document.getElementById("resultado").innerHTML =
            "Error al subir el archivo.";

    }

}