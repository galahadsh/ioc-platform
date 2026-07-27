import { subirArchivo } from "./upload.js";
import { cargarDashboard } from "./dashboard.js";
import { cargarHistorial } from "./history.js";

window.subirArchivo = subirArchivo;

document.addEventListener("DOMContentLoaded", async () => {

    await cargarDashboard();
    await cargarHistorial();

});