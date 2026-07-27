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

    const response = await fetch("/api/stats");

    if (!response.ok) {
        throw new Error("Error obteniendo estadísticas.");
    }

    return await response.json();
}

export async function getMaliciousIOCs() {

    const response = await fetch("/api/iocs/malicious");

    if (!response.ok) {
        throw new Error("Error obteniendo IOC.");
    }

    return await response.json();
}

export async function getHistory() {

    const response = await fetch("/api/analysis/history");

    if (!response.ok) {
        throw new Error("Error obteniendo historial.");
    }

    return await response.json();
}