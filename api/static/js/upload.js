import { uploadIOC } from "./api.js";


let uploadConfigured = false;
let uploadInProgress = false;


function getUploadElements() {
    return {
        input:
            document.getElementById("archivo") ??
            document.getElementById("uw-file-input"),

        button:
            document.getElementById("subir-archivo") ??
            document.getElementById("uw-import-button"),

        result:
            document.getElementById("resultado") ??
            document.getElementById("uw-message"),
    };
}


function showUploadMessage(
    message,
    type = "info"
) {
    const { result } = getUploadElements();

    if (!result) {
        console.log(message);
        return;
    }

    result.hidden = false;
    result.textContent = message;

    result.classList.remove(
        "upload-result-success",
        "upload-result-error",
        "upload-result-info",
        "is-success",
        "is-error",
        "is-info"
    );

    if (type === "success") {
        result.classList.add(
            "upload-result-success",
            "is-success"
        );
    } else if (type === "error") {
        result.classList.add(
            "upload-result-error",
            "is-error"
        );
    } else {
        result.classList.add(
            "upload-result-info",
            "is-info"
        );
    }
}


function setUploadButtonLoading(loading) {
    const { button } = getUploadElements();

    if (!button) {
        return;
    }

    button.disabled = loading;

    if (button.id === "uw-import-button") {
        button.textContent = loading
            ? "Importando…"
            : "Importar dataset";
    } else {
        button.textContent = loading
            ? "Subiendo…"
            : "Subir archivo";
    }
}


async function refreshPlatformData() {
    try {
        const dashboardModule = await import(
            "./dashboard.js"
        );

        const operations = [];

        if (
            typeof dashboardModule.cargarIOCs ===
            "function"
        ) {
            operations.push(
                dashboardModule.cargarIOCs()
            );
        }

        if (
            typeof dashboardModule.cargarDashboard ===
            "function"
        ) {
            operations.push(
                dashboardModule.cargarDashboard()
            );
        }

        await Promise.allSettled(operations);
    } catch (error) {
        console.warn(
            "No se pudieron refrescar las vistas:",
            error
        );
    }
}


async function handleUpload() {
    if (uploadInProgress) {
        return;
    }

    const {
        input,
        button
    } = getUploadElements();

    if (!input) {
        showUploadMessage(
            "No se encontró el selector de archivo.",
            "error"
        );
        return;
    }

    if (!input.files?.length) {
        showUploadMessage(
            "Selecciona un archivo CSV antes de importar.",
            "error"
        );
        return;
    }

    const file = input.files[0];

    if (
        !file.name
            .toLowerCase()
            .endsWith(".csv")
    ) {
        showUploadMessage(
            "El archivo seleccionado debe ser CSV.",
            "error"
        );
        return;
    }

    const formData = new FormData();

    /*
     * El endpoint actual espera el parámetro "file".
     */
    formData.append("file", file);

    uploadInProgress = true;
    setUploadButtonLoading(true);

    showUploadMessage(
        `Importando ${file.name}…`,
        "info"
    );

    try {
        const response = await uploadIOC(
            formData
        );

        showUploadMessage(
            response.message ??
            response.detail ??
            "Archivo importado correctamente.",
            "success"
        );

        input.value = "";

        if (button) {
            button.disabled = false;
        }

        await refreshPlatformData();

    } catch (error) {
        console.error(
            "Error durante la importación:",
            error
        );

        showUploadMessage(
            error.message ??
            "No fue posible importar el archivo.",
            "error"
        );

    } finally {
        uploadInProgress = false;
        setUploadButtonLoading(false);
    }
}


function handleFileSelected(input) {
    const file = input.files?.[0];

    if (!file) {
        return;
    }

    showUploadMessage(
        `Archivo seleccionado: ${file.name}`,
        "info"
    );

    const wizardButton =
        document.getElementById(
            "uw-import-button"
        );

    if (wizardButton) {
        wizardButton.disabled = false;
    }
}


export function configurarUpload() {
    if (uploadConfigured) {
        return;
    }

    uploadConfigured = true;

    /*
     * Delegación de eventos:
     * funciona aunque explorer.html o upload.html
     * sean cargados después mediante el router.
     */
    document.addEventListener(
        "click",
        (event) => {
            const button = event.target.closest(
                "#subir-archivo, #uw-import-button"
            );

            if (!button) {
                return;
            }

            event.preventDefault();
            handleUpload();
        }
    );

    document.addEventListener(
        "change",
        (event) => {
            const input = event.target.closest(
                "#archivo, #uw-file-input"
            );

            if (!input) {
                return;
            }

            handleFileSelected(input);
        }
    );

    console.log(
        "Módulo de carga IOC configurado."
    );
}


/*
 * Se configura al importar el módulo.
 */
configurarUpload();
