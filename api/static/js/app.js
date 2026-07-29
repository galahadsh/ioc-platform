import {
    initializeRouter
} from "./core/router.js";

import {
    cargarDashboard,
    configurarIOCExplorer
} from "./dashboard.js";

import {
    cargarHistorial
} from "./history.js";

import {
    cargarEstadisticas
} from "./statistics.js?v=20260729-5";


function initializeDashboardView() {
    cargarDashboard();
}


function initializeExplorerView() {
    configurarIOCExplorer();

    const uploadButton =
        document.getElementById("subir-archivo");

    if (
        uploadButton &&
        typeof window.subirArchivo === "function"
    ) {
        uploadButton.addEventListener(
            "click",
            window.subirArchivo
        );
    }
}


function initializeAnalysisView() {
    cargarHistorial();
}


function initializeStatisticsView() {
    document
        .getElementById("refresh-statistics")
        ?.addEventListener(
            "click",
            cargarEstadisticas
        );

    cargarEstadisticas();
}


document.addEventListener(
    "iocplatform:view-loaded",
    (event) => {
        const moduleName =
            event.detail?.module;

        switch (moduleName) {
            case "dashboard":
                initializeDashboardView();
                break;

            case "explorer":
                initializeExplorerView();
                break;

            case "analysis":
                initializeAnalysisView();
                break;

            case "statistics":
                initializeStatisticsView();
                break;

            default:
                break;
        }
    }
);


document.addEventListener(
    "DOMContentLoaded",
    () => {
        initializeRouter();
    }
);
