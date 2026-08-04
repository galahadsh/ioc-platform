console.log(
    "IOC Detail Component cargado."
);

let panel = null;
let activeRequestController = null;


function getElement(id) {
    return document.getElementById(id);
}


function setText(id, value) {
    const target = getElement(id);

    if (target) {
        target.textContent =
            value ?? "--";
    }
}


function ensurePanel() {
    if (
        panel &&
        document.body.contains(panel)
    ) {
        return panel;
    }

    panel = getElement(
        "ioc-detail-panel"
    );

    return panel;
}


function setLoadingState(isLoading) {
    const target = ensurePanel();

    if (!target) {
        return;
    }

    target.classList.toggle(
        "ioc-detail-loading",
        isLoading
    );

    target.setAttribute(
        "aria-busy",
        String(isLoading)
    );
}


function classifyIOC(vt) {
    const estado = String(
        vt?.estado ?? ""
    ).toLowerCase();

    if (estado === "error") {
        return {
            className: "unknown",
            label: "ERROR"
        };
    }

    if (
        estado === "pendiente" ||
        estado === "pending"
    ) {
        return {
            className: "pending",
            label: "PENDING"
        };
    }

    if (
        Number(vt?.malicious ?? 0) > 0
    ) {
        return {
            className: "malicious",
            label: "MALICIOUS"
        };
    }

    if (
        Number(vt?.suspicious ?? 0) > 0
    ) {
        return {
            className: "suspicious",
            label: "SUSPICIOUS"
        };
    }

    if (estado === "analizado") {
        return {
            className: "clean",
            label: "CLEAN"
        };
    }

    return {
        className: "unknown",
        label: "UNKNOWN"
    };
}


function renderStatus(vt) {
    const badge = getElement(
        "ioc-status"
    );

    if (!badge) {
        return;
    }

    const classification =
        classifyIOC(vt);

    badge.className =
        "status-badge " +
        classification.className;

    badge.textContent =
        classification.label;
}


function render(data) {
    const ioc = data?.ioc ?? {};
    const vt =
        data?.virustotal ?? {};

    const geo =
        data?.geolocation ?? {};

    setText(
        "ioc-value",
        ioc.valor
    );

    setText(
        "ioc-type",
        String(
            ioc.tipo ?? "IOC"
        ).toUpperCase()
    );

    renderStatus(vt);

    setText(
        "vt-score",
        vt.score ?? 0
    );

    setText(
        "vt-malicious",
        vt.malicious ?? 0
    );

    setText(
        "vt-suspicious",
        vt.suspicious ?? 0
    );

    setText(
        "vt-harmless",
        vt.harmless ?? 0
    );

    setText(
        "geo-country",
        geo.country
    );

    setText(
        "geo-region",
        geo.region
    );

    setText(
        "geo-city",
        geo.city
    );

    setText(
        "geo-asn",
        geo.asn
    );

    setText(
        "geo-isp",
        geo.isp
    );

    setText(
        "campaign-name",
        data?.campaign?.name
    );

    setText(
        "malware-name",
        data?.malware?.family
    );

    setText(
        "actor-name",
        data?.actor?.name
    );
}


function renderError(message) {
    setText(
        "ioc-value",
        "No fue posible cargar el IOC"
    );

    setText(
        "ioc-type",
        "ERROR"
    );

    const badge = getElement(
        "ioc-status"
    );

    if (badge) {
        badge.className =
            "status-badge unknown";

        badge.textContent =
            "ERROR";
    }

    console.error(message);
}


export async function openIOCDetail(
    iocId
) {
    const target = ensurePanel();

    if (!target) {
        console.error(
            "IOC Detail Panel no encontrado."
        );

        return;
    }

    target.classList.add("open");

    target.setAttribute(
        "aria-hidden",
        "false"
    );

    document.body.classList.add(
        "ioc-panel-open"
    );

    if (activeRequestController) {
        activeRequestController.abort();
    }

    activeRequestController =
        new AbortController();

    setLoadingState(true);

    try {
        const response = await fetch(
            `/api/v2/iocs/${iocId}/details`,
            {
                cache: "no-store",
                signal:
                    activeRequestController.signal
            }
        );

        if (!response.ok) {
            let detail =
                `HTTP ${response.status}`;

            try {
                const errorData =
                    await response.json();

                detail =
                    errorData.detail ??
                    detail;
            } catch {
                // La respuesta no era JSON.
            }

            throw new Error(detail);
        }

        const data =
            await response.json();

        render(data);

    } catch (error) {
        if (
            error.name ===
            "AbortError"
        ) {
            return;
        }

        renderError(
            error.message ??
            "Error consultando el IOC."
        );

    } finally {
        setLoadingState(false);
    }
}


export function closeIOCDetail() {
    const target = ensurePanel();

    if (!target) {
        return;
    }

    if (activeRequestController) {
        activeRequestController.abort();
        activeRequestController = null;
    }

    target.classList.remove("open");

    target.setAttribute(
        "aria-hidden",
        "true"
    );

    document.body.classList.remove(
        "ioc-panel-open"
    );

    document
        .querySelectorAll(
            "#tabla tr[data-ioc-id]"
        )
        .forEach((row) => {
            row.classList.remove(
                "ioc-row-selected"
            );
        });
}


document.addEventListener(
    "click",
    (event) => {
        if (
            event.target.closest(
                "#close-ioc-panel"
            )
        ) {
            closeIOCDetail();
        }
    }
);


document.addEventListener(
    "keydown",
    (event) => {
        if (event.key === "Escape") {
            closeIOCDetail();
        }
    }
);


window.openIOCDetail =
    openIOCDetail;

window.closeIOCDetail =
    closeIOCDetail;
