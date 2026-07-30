export async function uploadIOC(formData) {
    const response = await fetch("/api/upload", {
        method: "POST",
        body: formData
    });

    if (!response.ok) {
        throw new Error("Error al subir el archivo.");
    }

    return await response.json();
}


export async function getStats() {
    const response = await fetch(
        "/api/v2/iocs/dashboard",
        {
            cache: "no-store"
        }
    );

    if (!response.ok) {
        throw new Error(
            `Error obteniendo estadísticas: HTTP ${response.status}`
        );
    }

    const data = await response.json();

    return {
        total: data.total_iocs ?? 0,
        maliciosos: data.malicious ?? 0,
        sospechosos: data.suspicious ?? 0,
        limpios: data.harmless ?? 0,
        pendientes: data.undetected ?? 0,
        analizados: data.analizado ?? 0,
        errores: data.errores ?? 0
    };
}


export async function getMaliciousIOCs() {
    const response = await fetch(
        "/api/iocs/malicious"
    );

    if (!response.ok) {
        throw new Error("Error obteniendo IOC.");
    }

    return await response.json();
}


export async function getIOCs(filters = {}) {
    const params = new URLSearchParams();

    Object.entries(filters).forEach(
        ([key, value]) => {
            if (
                value !== undefined &&
                value !== null &&
                value !== ""
            ) {
                params.set(key, value);
            }
        }
    );

    const response = await fetch(
        `/api/iocs?${params.toString()}`
    );

    if (!response.ok) {
        throw new Error(
            "Error obteniendo la lista de IOC."
        );
    }

    return await response.json();
}


export function getIOCExportURL(filters = {}) {
    const params = new URLSearchParams();

    Object.entries(filters).forEach(
        ([key, value]) => {
            if (
                value !== undefined &&
                value !== null &&
                value !== ""
            ) {
                params.set(key, value);
            }
        }
    );

    return `/api/iocs/export?${params.toString()}`;
}


export async function getHistory() {
    const response = await fetch(
        "/api/analysis/history"
    );

    if (!response.ok) {
        throw new Error(
            "Error obteniendo historial."
        );
    }

    return await response.json();
}

export async function getStatisticsOverview() {
    const response = await fetch("/api/stats/overview");

    if (!response.ok) {
        throw new Error(
            `Error obteniendo estadísticas: ${response.status}`
        );
    }

    return response.json();
}