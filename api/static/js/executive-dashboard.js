import {
    getStats,
    getStatisticsOverview
} from "./api.js";


function element(id) {
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


function number(value) {
    return Number(value ?? 0);
}


function formatNumber(value) {
    return number(value).toLocaleString("es-MX");
}


function percentage(value, total) {
    const safeTotal = number(total);

    if (safeTotal <= 0) {
        return 0;
    }

    return (number(value) / safeTotal) * 100;
}


function setText(id, value) {
    const target = element(id);

    if (target) {
        target.textContent = value;
    }
}


function setWidth(id, value) {
    const target = element(id);

    if (target) {
        target.style.width =
            `${Math.min(Math.max(value, 0), 100)}%`;
    }
}


function updateKPIs(stats) {
    const total = number(stats.total);
    const malicious = number(stats.maliciosos);
    const suspicious = number(stats.sospechosos);
    const clean = number(stats.limpios);
    const pending = number(stats.pendientes);
    const errors = number(stats.errores);
    const analyzed = number(
        stats.analizados ??
        malicious + suspicious + clean
    );

    setText("ed-total", formatNumber(total));
    setText("ed-malicious", formatNumber(malicious));
    setText("ed-suspicious", formatNumber(suspicious));
    setText("ed-clean", formatNumber(clean));
    setText("ed-pending", formatNumber(pending));
    setText("ed-errors", formatNumber(errors));
    setText("ed-analyzed", formatNumber(analyzed));

    const maliciousPercent =
        percentage(malicious, total);

    const suspiciousPercent =
        percentage(suspicious, total);

    const cleanPercent =
        percentage(clean, total);

    const pendingPercent =
        percentage(pending, total);

    const errorsPercent =
        percentage(errors, total);

    const analyzedPercent =
        percentage(analyzed, total);

    setText(
        "ed-malicious-percent",
        `${maliciousPercent.toFixed(1)}% del total`
    );

    setText(
        "ed-suspicious-percent",
        `${suspiciousPercent.toFixed(1)}% del total`
    );

    setText(
        "ed-clean-percent",
        `${cleanPercent.toFixed(1)}% del total`
    );

    setText(
        "ed-pending-percent",
        `${pendingPercent.toFixed(1)}% del total`
    );

    setText(
        "ed-errors-percent",
        `${errorsPercent.toFixed(1)}% del total`
    );

    setText(
        "ed-analyzed-percent",
        `${analyzedPercent.toFixed(1)}% del total`
    );

    setText(
        "ed-malicious-rate",
        `${maliciousPercent.toFixed(1)}%`
    );

    setText(
        "ed-malicious-rate-detail",
        `${formatNumber(malicious)} de ` +
        `${formatNumber(analyzed)} analizados`
    );

    setWidth(
        "ed-analyzed-progress",
        analyzedPercent
    );

    setWidth(
        "ed-malicious-rate-progress",
        maliciousPercent
    );
}


function renderTypeDistribution(items) {
    const target = element("ed-type-distribution");

    if (!target) {
        return;
    }

    if (!Array.isArray(items) || !items.length) {
        target.innerHTML = `
            <div class="ed-empty">
                No hay datos por tipo.
            </div>
        `;

        return;
    }

    const colors = [
        "#1683ff",
        "#35d784",
        "#f39c21",
        "#a45bff",
        "#12a8e8",
        "#ff405d"
    ];

    const total = items.reduce(
        (sum, item) =>
            sum + number(item.total),
        0
    );

    let accumulated = 0;

    const segments = items.map(
        (item, index) => {
            const start = accumulated;
            const amount =
                percentage(item.total, total);

            accumulated += amount;

            return (
                `${colors[index % colors.length]} ` +
                `${start}% ${accumulated}%`
            );
        }
    );

    const legend = items.map(
        (item, index) => {
            const itemPercent =
                percentage(item.total, total);

            return `
                <div class="ed-legend-row">
                    <i
                        class="ed-legend-dot"
                        style="--legend-color:
                            ${colors[index % colors.length]}"
                    ></i>

                    <span>
                        ${escapeHTML(item.label)}
                    </span>

                    <strong>
                        ${formatNumber(item.total)}
                        (${itemPercent.toFixed(1)}%)
                    </strong>
                </div>
            `;
        }
    ).join("");

    target.innerHTML = `
        <div
            class="ed-donut"
            style="--donut:
                conic-gradient(${segments.join(", ")})"
        >
            <div class="ed-donut-center">
                <strong>${formatNumber(total)}</strong>
                <span>Total IOC</span>
            </div>
        </div>

        <div class="ed-legend">
            ${legend}
        </div>
    `;
}


function renderSources(items) {
    const target = element("ed-sources");

    if (!target) {
        return;
    }

    if (!Array.isArray(items) || !items.length) {
        target.innerHTML = `
            <div class="ed-empty">
                No hay fuentes registradas.
            </div>
        `;

        return;
    }

    const total = items.reduce(
        (sum, item) =>
            sum + number(item.total),
        0
    );

    target.innerHTML = items
        .slice(0, 6)
        .map((item) => {
            const itemPercent =
                percentage(item.total, total);

            return `
                <div class="ed-source-row">
                    <div class="ed-source-top">
                        <span>
                            ${escapeHTML(
                                item.label ??
                                "Sin fuente"
                            )}
                        </span>

                        <strong>
                            ${formatNumber(item.total)}
                            (${itemPercent.toFixed(1)}%)
                        </strong>
                    </div>

                    <div class="ed-source-track">
                        <span
                            style="width:
                                ${itemPercent}%"
                        ></span>
                    </div>
                </div>
            `;
        })
        .join("");
}


function monthLabel(value) {
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
            month: "short"
        }
    ).format(date);
}


function renderMonthlyBars(items) {
    const target = element("ed-monthly-bars");

    if (!target) {
        return;
    }

    if (!Array.isArray(items) || !items.length) {
        target.innerHTML = `
            <div class="ed-empty">
                No hay actividad mensual.
            </div>
        `;

        return;
    }

    const maximum = Math.max(
        ...items.map(
            (item) => number(item.total)
        ),
        1
    );

    target.innerHTML = items
        .slice(-10)
        .map((item) => {
            const height =
                Math.max(
                    number(item.total) /
                    maximum * 100,
                    2
                );

            return `
                <div class="ed-month-column">
                    <strong class="ed-month-value">
                        ${formatNumber(item.total)}
                    </strong>

                    <div class="ed-month-bar-space">
                        <div
                            class="ed-month-bar"
                            style="height: ${height}%"
                        ></div>
                    </div>

                    <span class="ed-month-label">
                        ${escapeHTML(
                            monthLabel(item.label)
                        )}
                    </span>
                </div>
            `;
        })
        .join("");
}


function renderTrend(items) {
    const target = element("ed-trend");

    if (!target) {
        return;
    }

    if (!Array.isArray(items) || !items.length) {
        target.innerHTML = `
            <div class="ed-empty">
                No hay información de tendencia.
            </div>
        `;

        return;
    }

    const values = items
        .slice(-10)
        .map((item) => number(item.total));

    const maximum = Math.max(...values, 1);
    const minimum = Math.min(...values, 0);
    const width = 700;
    const height = 210;

    const points = values.map(
        (value, index) => {
            const x = values.length === 1
                ? width / 2
                : (
                    index /
                    (values.length - 1)
                ) * width;

            const range =
                maximum - minimum || 1;

            const y =
                height -
                (
                    (value - minimum) /
                    range
                ) * (height - 25);

            return {
                x,
                y
            };
        }
    );

    const polyline = points
        .map((point) =>
            `${point.x},${point.y}`
        )
        .join(" ");

    const area =
        `0,${height} ` +
        `${polyline} ` +
        `${width},${height}`;

    const labels = items
        .slice(-10)
        .map((item) => `
            <span>
                ${escapeHTML(
                    monthLabel(item.label)
                )}
            </span>
        `)
        .join("");

    target.innerHTML = `
        <div class="ed-trend-chart">
            <svg
                viewBox="0 0 ${width} ${height}"
                preserveAspectRatio="none"
            >
                <defs>
                    <linearGradient
                        id="edGradient"
                        x1="0"
                        y1="0"
                        x2="0"
                        y2="1"
                    >
                        <stop
                            offset="0%"
                            stop-color="#1683ff"
                            stop-opacity="0.7"
                        />
                        <stop
                            offset="100%"
                            stop-color="#1683ff"
                            stop-opacity="0"
                        />
                    </linearGradient>
                </defs>

                <g class="ed-trend-grid">
                    <line
                        x1="0"
                        y1="25%"
                        x2="100%"
                        y2="25%"
                    />
                    <line
                        x1="0"
                        y1="50%"
                        x2="100%"
                        y2="50%"
                    />
                    <line
                        x1="0"
                        y1="75%"
                        x2="100%"
                        y2="75%"
                    />
                </g>

                <polygon
                    class="ed-trend-area"
                    points="${area}"
                />

                <polyline
                    class="ed-trend-line"
                    points="${polyline}"
                />
            </svg>

            <div class="ed-trend-labels">
                ${labels}
            </div>
        </div>
    `;
}


async function renderActivity() {
    const target = element("ed-activity");

    if (!target) {
        return;
    }

    try {
        const response = await fetch(
            "/api/analysis/history",
            {
                cache: "no-store"
            }
        );

        if (!response.ok) {
            throw new Error(
                `HTTP ${response.status}`
            );
        }

        const data = await response.json();
        const items = Array.isArray(data)
            ? data
            : data.items ?? [];

        if (!items.length) {
            target.innerHTML = `
                <div class="ed-empty">
                    Todavía no hay actividad registrada.
                </div>
            `;

            return;
        }

        target.innerHTML = items
            .slice(0, 6)
            .map((item) => `
                <div class="ed-activity-item">
                    <div class="ed-activity-icon">
                        ${
                            item.estado === "error"
                                ? "×"
                                : "⇧"
                        }
                    </div>

                    <div class="ed-activity-text">
                        <strong>
                            ${escapeHTML(
                                item.nombre_archivo ??
                                item.archivo ??
                                "Análisis IOC"
                            )}
                        </strong>

                        <span>
                            ${formatNumber(
                                item.total_iocs ?? 0
                            )}
                            IOC ·
                            ${formatNumber(
                                item.maliciosos ?? 0
                            )}
                            maliciosos
                        </span>
                    </div>

                    <span class="ed-activity-time">
                        ${escapeHTML(
                            item.estado ??
                            "Finalizado"
                        )}
                    </span>
                </div>
            `)
            .join("");

    } catch (error) {
        console.error(error);

        target.innerHTML = `
            <div class="ed-empty">
                No fue posible cargar la actividad.
            </div>
        `;
    }
}


function updateTimestamp() {
    setText(
        "ed-last-update",
        new Intl.DateTimeFormat(
            "es-MX",
            {
                dateStyle: "medium",
                timeStyle: "medium"
            }
        ).format(new Date())
    );
}


function setLoading(loading) {
    const button = element("ed-refresh");

    if (!button) {
        return;
    }

    button.disabled = loading;
    button.innerHTML = loading
        ? "<span>↻</span> Actualizando…"
        : "<span>↻</span> Actualizar";
}


function showError(message) {
    const target = element("ed-error");

    if (!target) {
        return;
    }

    target.textContent = message;
    target.hidden = false;
}


function hideError() {
    const target = element("ed-error");

    if (!target) {
        return;
    }

    target.textContent = "";
    target.hidden = true;
}


export async function cargarExecutiveDashboard() {
    setLoading(true);
    hideError();

    try {
        const [
            stats,
            overview
        ] = await Promise.all([
            getStats(),
            getStatisticsOverview()
        ]);

        updateKPIs(stats);

        renderTypeDistribution(
            overview.by_type ?? []
        );

        renderSources(
            overview.by_source ?? []
        );

        renderMonthlyBars(
            overview.by_month ?? []
        );

        renderTrend(
            overview.by_month ?? []
        );

        await renderActivity();
        updateTimestamp();

        element("ed-refresh")
            ?.addEventListener(
                "click",
                cargarExecutiveDashboard,
                {
                    once: true
                }
            );

        element("ed-export-csv")
            ?.addEventListener(
                "click",
                () => {
                    window.location.href =
                        "/api/iocs/export";
                },
                {
                    once: true
                }
            );

    } catch (error) {
        console.error(error);

        showError(
            "No fue posible cargar la información " +
            "del Dashboard."
        );
    } finally {
        setLoading(false);
    }
}
