let statusTimer = null;


function element(id) {
    return document.getElementById(id);
}


function formatNumber(value) {
    return Number(
        value ?? 0
    ).toLocaleString("es-MX");
}


function showMessage(
    message,
    type = "info",
) {
    const target =
        element("vt-control-message");

    if (!target) {
        return;
    }

    target.hidden = false;
    target.textContent = message;
    target.dataset.type = type;
}


function updateProgress(data) {
    const total =
        Number(data.total_items ?? 0);

    const processed =
        Number(data.processed_items ?? 0);

    const percentage = total > 0
        ? Math.min(
            processed / total * 100,
            100,
        )
        : 0;

    const progress =
        element("vt-progress-bar");

    if (progress) {
        progress.style.width =
            `${percentage}%`;
    }

    const text =
        element("vt-progress-text");

    if (text) {
        text.textContent =
            `${formatNumber(processed)} de ` +
            `${formatNumber(total)} ` +
            `(${percentage.toFixed(1)}%)`;
    }

    const status =
        element("vt-job-status");

    if (status) {
        status.textContent =
            data.status ?? "idle";

        status.dataset.status =
            data.status ?? "idle";
    }

    const summary = data.summary ?? {};

    const pending =
        element("vt-pending-count");

    const analyzed =
        element("vt-analyzed-count");

    const errors =
        element("vt-errors-count");

    if (pending) {
        pending.textContent =
            formatNumber(summary.pending);
    }

    if (analyzed) {
        analyzed.textContent =
            formatNumber(summary.analyzed);
    }

    if (errors) {
        errors.textContent =
            formatNumber(summary.errors);
    }

    const startButton =
        element("start-virustotal-analysis");

    if (startButton) {
        startButton.disabled = [
            "pending",
            "running",
        ].includes(data.status);
    }

    if (
        data.status === "completed" ||
        data.status === "failed"
    ) {
        stopStatusPolling();
    }
}


async function loadVirusTotalStatus() {
    try {
        const response = await fetch(
            "/api/enrichment/virustotal/status",
            {
                cache: "no-store",
            },
        );

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                data.detail ??
                `HTTP ${response.status}`
            );
        }

        updateProgress(data);

    } catch (error) {
        console.error(error);

        showMessage(
            "No fue posible consultar el estado.",
            "error",
        );
    }
}


async function startVirusTotalAnalysis() {
    const button =
        element("start-virustotal-analysis");

    if (button) {
        button.disabled = true;
        button.textContent =
            "Enviando solicitud…";
    }

    try {
        const response = await fetch(
            "/api/enrichment/virustotal/start",
            {
                method: "POST",
                cache: "no-store",
            },
        );

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                data.detail ??
                `HTTP ${response.status}`
            );
        }

        showMessage(
            data.message,
            data.started
                ? "success"
                : "info",
        );

        await loadVirusTotalStatus();

        if (data.started) {
            startStatusPolling();
        }

    } catch (error) {
        console.error(error);

        showMessage(
            error.message ??
            "No fue posible iniciar el análisis.",
            "error",
        );

    } finally {
        if (button) {
            button.textContent =
                "Iniciar análisis en VirusTotal";
        }
    }
}


async function retryVirusTotalErrors() {
    try {
        const response = await fetch(
            "/api/enrichment/virustotal/retry-errors",
            {
                method: "POST",
                cache: "no-store",
            },
        );

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                data.detail ??
                `HTTP ${response.status}`
            );
        }

        showMessage(
            `${data.message} ` +
            `${formatNumber(data.updated)} IOC.`,
            "success",
        );

        await loadVirusTotalStatus();

    } catch (error) {
        console.error(error);

        showMessage(
            error.message,
            "error",
        );
    }
}


function startStatusPolling() {
    stopStatusPolling();

    statusTimer = window.setInterval(
        loadVirusTotalStatus,
        5000,
    );
}


function stopStatusPolling() {
    if (statusTimer !== null) {
        window.clearInterval(
            statusTimer
        );

        statusTimer = null;
    }
}


function configureEnrichmentControls() {
    document.addEventListener(
        "click",
        (event) => {
            if (
                event.target.closest(
                    "#start-virustotal-analysis"
                )
            ) {
                startVirusTotalAnalysis();
            }

            if (
                event.target.closest(
                    "#refresh-virustotal-status"
                )
            ) {
                loadVirusTotalStatus();
            }

            if (
                event.target.closest(
                    "#retry-virustotal-errors"
                )
            ) {
                retryVirusTotalErrors();
            }
        },
    );

    document.addEventListener(
        "iocplatform:view-loaded",
        () => {
            if (
                element(
                    "start-virustotal-analysis"
                )
            ) {
                loadVirusTotalStatus();
            }
        },
    );
}


configureEnrichmentControls();
