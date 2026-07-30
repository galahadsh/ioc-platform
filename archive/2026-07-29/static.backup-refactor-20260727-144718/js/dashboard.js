import {
    getStats,
    getIOCs,
    getIOCExportURL
} from "./api.js";


const state = {
    page: 1,
    pageSize: 25,
    totalPages: 0,
    total: 0
};


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


function formatDate(value) {
    if (!value) {
        return "-";
    }

    const date = new Date(value);

    if (Number.isNaN(date.getTime())) {
        return value;
    }

    return date.toLocaleString("es-MX");
}


function getFilters(includePagination = true) {
    const filters = {
        search: getElement("ioc-search")?.value.trim(),
        tipo: getElement("ioc-tipo")?.value,
        estado: getElement("ioc-estado")?.value,
        fuente: getElement("ioc-fuente")?.value.trim(),
        campaign: getElement("ioc-campaign")?.value.trim(),
        malware_family:
            getElement("ioc-malware-family")?.value.trim(),
        date_from: getElement("ioc-date-from")?.value,
        date_to: getElement("ioc-date-to")?.value
    };

    if (includePagination) {
        filters.page = state.page;
        filters.page_size = state.pageSize;
    }

    return filters;
}


function renderIOCStatus(status) {
    const normalized = String(
        status ?? "sin estado"
    )
        .toLowerCase()
        .replaceAll(" ", "-");

    return `
        <span class="status-badge status-${escapeHTML(normalized)}">
            ${escapeHTML(status ?? "Sin estado")}
        </span>
    `;
}


function renderIOCs(items) {
    const table = getElement("tabla");

    if (!table) {
        return;
    }

    table.innerHTML = "";

    if (!Array.isArray(items) || !items.length) {
        table.innerHTML = `
            <tr>
                <td colspan="10" class="empty-state">
                    No se encontraron IOC con los filtros
                    seleccionados.
                </td>
            </tr>
        `;

        return;
    }

    const rows = items.map((ioc) => `
        <tr>
            <td>${escapeHTML(ioc.tipo ?? "-")}</td>

            <td class="ioc-value">
                ${escapeHTML(ioc.valor ?? "-")}
            </td>

            <td>
                ${escapeHTML(
                    ioc.campaign ?? "Sin campaña"
                )}
            </td>

            <td>
                ${escapeHTML(
                    ioc.malware_family ??
                    "No identificado"
                )}
            </td>

            <td>
                ${renderIOCStatus(ioc.vt_estado)}
            </td>

            <td>
                ${escapeHTML(ioc.vt_score ?? 0)}
            </td>

            <td>
                ${escapeHTML(
                    ioc.vt_malicious ?? 0
                )}
            </td>

            <td>
                ${escapeHTML(
                    ioc.vt_suspicious ?? 0
                )}
            </td>

            <td>
                ${escapeHTML(ioc.fuente ?? "-")}
            </td>

            <td>
                ${escapeHTML(
                    formatDate(ioc.ultima_consulta)
                )}
            </td>
        </tr>
    `);

    table.innerHTML = rows.join("");
}


function renderPagination(pagination) {
    if (!pagination) {
        return;
    }

    state.total = pagination.total ?? 0;
    state.totalPages = pagination.total_pages ?? 0;

    const firstItem =
        pagination.total === 0
            ? 0
            : (
                (pagination.page - 1) *
                pagination.page_size
            ) + 1;

    const lastItem = Math.min(
        pagination.page * pagination.page_size,
        pagination.total
    );

    const paginationInfo =
        getElement("ioc-pagination-info");

    if (paginationInfo) {
        paginationInfo.textContent =
            `Mostrando ${firstItem}-${lastItem} de ` +
            `${pagination.total} IOC`;
    }

    const pageNumber =
        getElement("ioc-page-number");

    if (pageNumber) {
        pageNumber.textContent =
            pagination.total_pages > 0
                ? (
                    `Página ${pagination.page} de ` +
                    `${pagination.total_pages}`
                )
                : "Página 0 de 0";
    }

    const previousButton =
        getElement("pagina-anterior");

    if (previousButton) {
        previousButton.disabled =
            !pagination.has_previous;
    }

    const nextButton =
        getElement("pagina-siguiente");

    if (nextButton) {
        nextButton.disabled =
            !pagination.has_next;
    }
}


function showIOCError(message) {
    const errorBox = getElement("ioc-error");

    if (!errorBox) {
        return;
    }

    errorBox.textContent = message;
    errorBox.hidden = false;
}


function hideIOCError() {
    const errorBox = getElement("ioc-error");

    if (!errorBox) {
        return;
    }

    errorBox.textContent = "";
    errorBox.hidden = true;
}


async function cargarStats() {
    const stats = await getStats();

    const total = getElement("total");
    const maliciosos = getElement("maliciosos");
    const sospechosos = getElement("sospechosos");
    const limpios = getElement("limpios");
    const pendientes = getElement("pendientes");
    const errores = getElement("errores");

    if (total) {
        total.textContent = stats.total ?? 0;
    }

    if (maliciosos) {
        maliciosos.textContent =
            stats.maliciosos ?? 0;
    }

    if (sospechosos) {
        sospechosos.textContent =
            stats.sospechosos ?? 0;
    }

    if (limpios) {
        limpios.textContent =
            stats.limpios ?? 0;
    }

    if (pendientes) {
        pendientes.textContent =
            stats.pendientes ?? 0;
    }

    if (errores) {
        errores.textContent =
            stats.errores ?? 0;
    }
}


export async function cargarIOCs() {
    try {
        hideIOCError();

        const response = await getIOCs(
            getFilters(true)
        );

        renderIOCs(response.items ?? []);
        renderPagination(
            response.pagination ?? {
                page: 1,
                page_size: state.pageSize,
                total: 0,
                total_pages: 0,
                has_previous: false,
                has_next: false
            }
        );

    } catch (error) {
        console.error(error);

        showIOCError(
            "No fue posible obtener los IOC."
        );
    }
}


function limpiarFiltros() {
    const fields = [
        "ioc-search",
        "ioc-tipo",
        "ioc-estado",
        "ioc-fuente",
        "ioc-campaign",
        "ioc-malware-family",
        "ioc-date-from",
        "ioc-date-to"
    ];

    for (const fieldId of fields) {
        const field = getElement(fieldId);

        if (field) {
            field.value = "";
        }
    }

    const pageSize =
        getElement("ioc-page-size");

    if (pageSize) {
        pageSize.value = "25";
    }

    state.page = 1;
    state.pageSize = 25;

    cargarIOCs();
}


function exportarIOCs() {
    const dateFrom =
        getElement("ioc-date-from")?.value;

    const dateTo =
        getElement("ioc-date-to")?.value;

    if (
        dateFrom &&
        dateTo &&
        dateFrom > dateTo
    ) {
        showIOCError(
            "La fecha inicial no puede ser mayor " +
            "que la fecha final."
        );

        return;
    }

    hideIOCError();

    const url = getIOCExportURL(
        getFilters(false)
    );

    window.location.href = url;
}


export function configurarIOCExplorer() {
    getElement("aplicar-filtros")
        ?.addEventListener("click", () => {
            state.page = 1;

            state.pageSize = Number(
                getElement("ioc-page-size")?.value
                ?? 25
            );

            cargarIOCs();
        });

    getElement("limpiar-filtros")
        ?.addEventListener(
            "click",
            limpiarFiltros
        );

    getElement("pagina-anterior")
        ?.addEventListener("click", () => {
            if (state.page > 1) {
                state.page -= 1;
                cargarIOCs();
            }
        });

    getElement("pagina-siguiente")
        ?.addEventListener("click", () => {
            if (state.page < state.totalPages) {
                state.page += 1;
                cargarIOCs();
            }
        });

    getElement("ioc-page-size")
        ?.addEventListener(
            "change",
            (event) => {
                state.page = 1;
                state.pageSize = Number(
                    event.target.value
                );

                cargarIOCs();
            }
        );

    getElement("exportar-iocs")
        ?.addEventListener(
            "click",
            exportarIOCs
        );

    getElement("ioc-search")
        ?.addEventListener(
            "keydown",
            (event) => {
                if (event.key === "Enter") {
                    state.page = 1;
                    cargarIOCs();
                }
            }
        );

    getElement("ioc-campaign")
        ?.addEventListener(
            "keydown",
            (event) => {
                if (event.key === "Enter") {
                    state.page = 1;
                    cargarIOCs();
                }
            }
        );

    getElement("ioc-malware-family")
        ?.addEventListener(
            "keydown",
            (event) => {
                if (event.key === "Enter") {
                    state.page = 1;
                    cargarIOCs();
                }
            }
        );
}


export async function cargarDashboard() {
    try {
        await Promise.all([
            cargarStats(),
            cargarIOCs()
        ]);
    } catch (error) {
        console.error(error);
    }
}
