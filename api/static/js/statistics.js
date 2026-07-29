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


function calculatePercentage(value, total) {
    const numericTotal = Number(total ?? 0);

    if (numericTotal <= 0) {
        return 0;
    }

    return (Number(value ?? 0) / numericTotal) * 100;
}


function setText(id, value) {
    const element = getElement(id);

    if (element) {
        element.textContent = formatNumber(value);
    }
}


function setPercentage(id, value) {
    const element = getElement(id);

    if (element) {
        element.textContent = `${value.toFixed(1)}%`;
    }
}


function setProgress(id, value) {
    const element = getElement(id);

    if (element) {
        const percentage = Math.min(
            Math.max(Number(value ?? 0), 0),
            100
        );

        element.style.width = `${percentage}%`;
    }
}


function updateSummary(summary) {
    const total = Number(summary.total ?? 0);

    const metrics = [
        {
            key: "malicious",
            value: Number(summary.maliciosos ?? 0)
        },
        {
            key: "suspicious",
            value: Number(summary.sospechosos ?? 0)
        },
        {
            key: "clean",
            value: Number(summary.limpios ?? 0)
        },
        {
            key: "pending",
            value: Number(summary.pendientes ?? 0)
        },
        {
            key: "errors",
            value: Number(summary.errores ?? 0)
        }
    ];

    setText("statistics-total", total);

    for (const metric of metrics) {
        const percentage = calculatePercentage(
            metric.value,
            total
        );

        setText(
            `statistics-${metric.key}`,
            metric.value
        );

        setPercentage(
            `statistics-${metric.key}-percent`,
            percentage
        );

        setProgress(
            `statistics-${metric.key}-progress`,
            percentage
        );
    }
}


function buildConicGradient(items, total) {
    const safeTotal = Math.max(Number(total ?? 0), 1);
    let accumulated = 0;

    const segments = items.map((item) => {
        const start = accumulated;
        const amount = (
            Number(item.total ?? 0) / safeTotal
        ) * 100;

        accumulated += amount;

        return `${item.color} ${start}% ${accumulated}%`;
    });

    if (accumulated < 100) {
        segments.push(
            `#132b3f ${accumulated}% 100%`
        );
    }

    return `conic-gradient(${segments.join(", ")})`;
}


function renderReputation(summary) {
    const container = getElement("statistics-reputation");

    if (!container) {
        return;
    }

    const total = Number(summary.total ?? 0);

    const items = [
        {
            label: "Maliciosos",
            total: Number(summary.maliciosos ?? 0),
            color: "#ff334f"
        },
        {
            label: "Sospechosos",
            total: Number(summary.sospechosos ?? 0),
            color: "#f5b800"
        },
        {
            label: "Limpios",
            total: Number(summary.limpios ?? 0),
            color: "#27df87"
        },
        {
            label: "Pendientes",
            total: Number(summary.pendientes ?? 0),
            color: "#a855f7"
        },
        {
            label: "Errores",
            total: Number(summary.errores ?? 0),
            color: "#ff6a2a"
        }
    ];

    const donutBackground = buildConicGradient(
        items,
        total
    );

    const legend = items.map((item) => {
        const percentage = calculatePercentage(
            item.total,
            total
        );

        return `
            <div class="ti-legend-item">
                <span
                    class="ti-legend-color"
                    style="--legend-color: ${item.color}"
                ></span>

                <div class="ti-legend-data">
                    <span>
                        ${escapeHTML(item.label)}
                    </span>

                    <strong>
                        ${formatNumber(item.total)}
                        (${percentage.toFixed(1)}%)
                    </strong>
                </div>
            </div>
        `;
    }).join("");

    container.innerHTML = `
        <div class="ti-reputation-layout">

            <div
                class="ti-donut"
                style="--donut-background: ${donutBackground}"
                role="img"
                aria-label="Distribución de reputación de IOC"
            >
                <div class="ti-donut-center">
                    <strong>${formatNumber(total)}</strong>
                    <span>Total</span>
                </div>
            </div>

            <div class="ti-legend">
                ${legend}
            </div>

        </div>
    `;
}


function renderTypeChart(items) {
    const container = getElement("statistics-types");

    if (!container) {
        return;
    }

    if (!Array.isArray(items) || items.length === 0) {
        container.innerHTML = `
            <div class="ti-empty">
                No hay información por tipo.
            </div>
        `;

        return;
    }

    const maximum = Math.max(
        ...items.map(
            (item) => Number(item.total ?? 0)
        ),
        1
    );

    container.innerHTML = items.map((item) => {
        const total = Number(item.total ?? 0);
        const width = Math.max(
            (total / maximum) * 100,
            1
        );

        return `
            <div class="ti-type-row">
                <span
                    class="ti-type-label"
                    title="${escapeHTML(item.label)}"
                >
                    ${escapeHTML(item.label)}
                </span>

                <div class="ti-type-track">
                    <div
                        class="ti-type-fill"
                        style="width: ${width}%"
                    ></div>
                </div>

                <strong class="ti-type-total">
                    ${formatNumber(total)}
                </strong>
            </div>
        `;
    }).join("");
}


function renderTable(
    containerId,
    items,
    firstColumn
) {
    const container = getElement(containerId);

    if (!container) {
        return;
    }

    if (!Array.isArray(items) || items.length === 0) {
        container.innerHTML = `
            <div class="ti-empty">
                No hay información disponible.
            </div>
        `;

        return;
    }

    const rows = items.map((item) => `
        <tr>
            <td>${escapeHTML(item.label)}</td>
            <td>${formatNumber(item.total)}</td>
        </tr>
    `).join("");

    container.innerHTML = `
        <table class="ti-data-table">
            <thead>
                <tr>
                    <th>${escapeHTML(firstColumn)}</th>
                    <th>IOC</th>
                </tr>
            </thead>

            <tbody>
                ${rows}
            </tbody>
        </table>
    `;
}


function formatMonthLabel(value) {
    const match = String(value ?? "")
        .match(/^(\d{4})-(\d{2})$/);

    if (!match) {
        return String(value ?? "");
    }

    const date = new Date(
        Number(match[1]),
        Number(match[2]) - 1,
        1
    );

    return new Intl.DateTimeFormat(
        "es-MX",
        {
            month: "short",
            year: "numeric"
        }
    ).format(date);
}


function renderMonthlyActivity(items) {
    const container = getElement("statistics-monthly");

    if (!container) {
        return;
    }

    if (!Array.isArray(items) || items.length === 0) {
        container.innerHTML = `
            <div class="ti-empty">
                No hay actividad mensual registrada.
            </div>
        `;

        return;
    }

    const maximum = Math.max(
        ...items.map(
            (item) => Number(item.total ?? 0)
        ),
        1
    );

    const columns = items.map((item) => {
        const total = Number(item.total ?? 0);

        const height = total > 0
            ? Math.max((total / maximum) * 100, 2)
            : 0;

        return `
            <div class="ti-month-column">
                <strong class="ti-month-value">
                    ${formatNumber(total)}
                </strong>

                <div class="ti-month-bar-space">
                    <div
                        class="ti-month-bar"
                        style="height: ${height}%"
                    ></div>
                </div>

                <span class="ti-month-label">
                    ${escapeHTML(
                        formatMonthLabel(item.label)
                    )}
                </span>
            </div>
        `;
    }).join("");

    container.innerHTML = `
        <div class="ti-monthly-chart">
            ${columns}
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


function updateTimestamp() {
    const element = getElement(
        "statistics-updated-at"
    );

    if (!element) {
        return;
    }

    element.textContent =
        new Intl.DateTimeFormat(
            "es-MX",
            {
                dateStyle: "medium",
                timeStyle: "medium"
            }
        ).format(new Date());
}


function setLoading(isLoading) {
    const button = getElement("refresh-statistics");

    if (!button) {
        return;
    }

    button.disabled = isLoading;

    button.innerHTML = isLoading
        ? "<span>↻</span> Actualizando…"
        : "<span>↻</span> Actualizar";
}


export async function cargarEstadisticas() {
    setLoading(true);
    hideStatisticsError();

    try {
        const data = await getStatisticsOverview();
        const summary = data.summary ?? {};

        updateSummary(summary);
        renderReputation(summary);
        renderTypeChart(data.by_type);

        renderTable(
            "statistics-sources",
            data.by_source,
            "Fuente"
        );

        renderTable(
            "statistics-campaigns",
            data.by_campaign,
            "Campaña"
        );

        renderTable(
            "statistics-malware",
            data.by_malware,
            "Familia"
        );

        renderMonthlyActivity(data.by_month);
        updateTimestamp();

    } catch (error) {
        console.error(
            "No fue posible cargar las estadísticas:",
            error
        );

        showStatisticsError(
            "No fue posible consultar las estadísticas. " +
            "Verifica que /api/stats/overview esté disponible."
        );
    } finally {
        setLoading(false);
    }
}
