import {
    getStatisticsOverview
} from "./api.js";


function getElement(id) {
    return document.getElementById(id);
}


function escapeHTML(value) {
    return String(value ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}


function formatNumber(value) {
    return Number(value ?? 0).toLocaleString("es-MX");
}


function setText(id, value) {
    const element = getElement(id);

    if (element) {
        element.textContent = formatNumber(value);
    }
}


function renderHorizontalBars(containerId, items) {
    const container = getElement(containerId);

    if (!container) {
        return;
    }

    if (!Array.isArray(items) || items.length === 0) {
        container.innerHTML = `
            <div class="statistics-empty">
                No hay información disponible.
            </div>
        `;

        return;
    }

    const maximum = Math.max(
        ...items.map((item) => Number(item.total ?? 0)),
        1
    );

    container.innerHTML = items.map((item) => {
        const total = Number(item.total ?? 0);
        const percentage = Math.max(
            (total / maximum) * 100,
            2
        );

        return `
            <div class="statistics-bar-item">
                <div class="statistics-bar-header">
                    <span>
                        ${escapeHTML(item.label)}
                    </span>

                    <strong>
                        ${formatNumber(total)}
                    </strong>
                </div>

                <div class="statistics-bar-track">
                    <div
                        class="statistics-bar-fill"
                        style="width: ${percentage}%"
                    ></div>
                </div>
            </div>
        `;
    }).join("");
}


function renderReputation(summary) {
    const container = getElement("statistics-reputation");

    if (!container) {
        return;
    }

    const items = [
        {
            label: "Maliciosos",
            total: summary.maliciosos ?? 0,
            className: "malicious"
        },
        {
            label: "Sospechosos",
            total: summary.sospechosos ?? 0,
            className: "suspicious"
        },
        {
            label: "Limpios",
            total: summary.limpios ?? 0,
            className: "clean"
        },
        {
            label: "Pendientes",
            total: summary.pendientes ?? 0,
            className: "pending"
        },
        {
            label: "Errores",
            total: summary.errores ?? 0,
            className: "error"
        }
    ];

    const total = Math.max(
        items.reduce(
            (accumulator, item) =>
                accumulator + Number(item.total),
            0
        ),
        1
    );

    container.innerHTML = items.map((item) => {
        const percentage = (
            Number(item.total) / total
        ) * 100;

        return `
            <div class="reputation-item">
                <div class="reputation-label">
                    <span
                        class="reputation-dot ${item.className}"
                    ></span>

                    <span>
                        ${escapeHTML(item.label)}
                    </span>
                </div>

                <div class="reputation-value">
                    <strong>
                        ${formatNumber(item.total)}
                    </strong>

                    <span>
                        ${percentage.toFixed(1)}%
                    </span>
                </div>
            </div>
        `;
    }).join("");
}


function renderMonthlyActivity(items) {
    const container = getElement("statistics-monthly");

    if (!container) {
        return;
    }

    if (!Array.isArray(items) || items.length === 0) {
        container.innerHTML = `
            <div class="statistics-empty">
                No hay actividad mensual registrada.
            </div>
        `;

        return;
    }

    const maximum = Math.max(
        ...items.map((item) => Number(item.total ?? 0)),
        1
    );

    container.innerHTML = `
        <div class="monthly-chart">
            ${items.map((item) => {
                const total = Number(item.total ?? 0);
                const height = Math.max(
                    (total / maximum) * 100,
                    4
                );

                return `
                    <div class="monthly-column">
                        <div class="monthly-value">
                            ${formatNumber(total)}
                        </div>

                        <div class="monthly-bar-wrapper">
                            <div
                                class="monthly-bar"
                                style="height: ${height}%"
                            ></div>
                        </div>

                        <div class="monthly-label">
                            ${escapeHTML(item.label)}
                        </div>
                    </div>
                `;
            }).join("")}
        </div>
    `;
}


function showStatisticsError(message) {
    const errorBox = getElement("statistics-error");

    if (!errorBox) {
        return;
    }

    errorBox.textContent = message;
    errorBox.hidden = false;
}


function hideStatisticsError() {
    const errorBox = getElement("statistics-error");

    if (!errorBox) {
        return;
    }

    errorBox.textContent = "";
    errorBox.hidden = true;
}


export async function cargarEstadisticas() {
    try {
        hideStatisticsError();

        const data = await getStatisticsOverview();
        const summary = data.summary ?? {};

        setText("statistics-total", summary.total);
        setText(
            "statistics-malicious",
            summary.maliciosos
        );
        setText(
            "statistics-suspicious",
            summary.sospechosos
        );
        setText(
            "statistics-clean",
            summary.limpios
        );
        setText(
            "statistics-pending",
            summary.pendientes
        );
        setText(
            "statistics-errors",
            summary.errores
        );

        renderReputation(summary);

        renderHorizontalBars(
            "statistics-types",
            data.by_type
        );

        renderHorizontalBars(
            "statistics-sources",
            data.by_source
        );

        renderHorizontalBars(
            "statistics-campaigns",
            data.by_campaign
        );

        renderHorizontalBars(
            "statistics-malware",
            data.by_malware
        );

        renderMonthlyActivity(data.by_month);

    } catch (error) {
        console.error(error);

        showStatisticsError(
            "No fue posible cargar las estadísticas."
        );
    }
}