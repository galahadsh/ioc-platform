export async function uploadIOC(formData) {
    const response = await fetch(
        "/api/upload",
        {
            method: "POST",
            body: formData,
            cache: "no-store"
        }
    );

    const contentType =
        response.headers.get(
            "content-type"
        ) ?? "";

    let payload;

    if (
        contentType.includes(
            "application/json"
        )
    ) {
        payload = await response.json();
    } else {
        payload = {
            detail: await response.text()
        };
    }

    if (!response.ok) {
        throw new Error(
            payload.detail ??
            payload.message ??
            `Error HTTP ${response.status}`
        );
    }

    return payload;
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
        `/api/v2/iocs?${params.toString()}`,
        { cache: "no-store" }
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

export async function getIOCDetail(iocId) {
    const response = await fetch(
        `/api/v2/iocs/${encodeURIComponent(iocId)}`,
        {
            cache: "no-store"
        }
    );

    if (!response.ok) {
        throw new Error(
            `Error obteniendo detalle del IOC: HTTP ${response.status}`
        );
    }

    return await response.json();
}
