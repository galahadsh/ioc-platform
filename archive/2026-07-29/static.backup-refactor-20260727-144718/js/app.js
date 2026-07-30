import {
    subirArchivo
} from "./upload.js";

import {
    cargarDashboard,
    configurarIOCExplorer
} from "./dashboard.js";

import {
    cargarHistorial
} from "./history.js";


window.subirArchivo = subirArchivo;


document.addEventListener(
    "DOMContentLoaded",
    async () => {
        configurarIOCExplorer();

        await Promise.all([
            cargarDashboard(),
            cargarHistorial()
        ]);
    }
);
