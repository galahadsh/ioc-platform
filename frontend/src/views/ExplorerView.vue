<template>
  <section class="explorer">

    <header class="explorer-header">
      <div>
        <span class="eyebrow">IOC MANAGEMENT</span>
        <h1>IOC Explorer</h1>
        <p>
          Consulta, filtra y analiza los indicadores
          almacenados en el repositorio central.
        </p>
      </div>

      <button
        type="button"
        class="action-button"
        :disabled="store.loading"
        @click="store.refresh()"
      >
        {{ store.loading ? "Actualizando..." : "↻ Actualizar" }}
      </button>
    </header>

    <section class="enterprise-panel">
      <div class="panel-heading">
        <div>
          <h2>Filtros de búsqueda</h2>
          <p>Refina los resultados del repositorio.</p>
        </div>
      </div>

      <form class="filter-grid" @submit.prevent="applyFilters">

        <label class="field field-wide">
          <span>Buscar IOC</span>
          <input
            v-model.trim="draft.search"
            type="search"
            placeholder="IP, dominio, URL, hash, campaña o malware"
          />
        </label>

        <label class="field">
          <span>Tipo</span>
          <select v-model="draft.tipo">
            <option value="">Todos</option>
            <option value="ip">IP</option>
            <option value="domain">Dominio</option>
            <option value="url">URL</option>
            <option value="hash">Hash</option>
          </select>
        </label>

        <label class="field">
          <span>Estado</span>
          <select v-model="draft.estado">
            <option value="">Todos</option>
            <option value="malicious">Malicioso</option>
            <option value="suspicious">Sospechoso</option>
            <option value="clean">Limpio</option>
            <option value="pending">Pendiente</option>
            <option value="error">Error</option>
          </select>
        </label>

        <label class="field">
          <span>País GeoIP (ISO-2)</span>
          <input
            v-model.trim="draft.country"
            maxlength="2"
            placeholder="Ej. CN, RU, US"
            @input="draft.country = draft.country.toUpperCase()"
          />
        </label>

        <label class="field">
          <span>Fuente</span>
          <input
            v-model.trim="draft.fuente"
            placeholder="Ej. SOCradar"
          />
        </label>

        <label class="field">
          <span>Campaña</span>
          <input
            v-model.trim="draft.campaign"
            placeholder="Ej. Akira"
          />
        </label>

        <label class="field">
          <span>Familia de malware</span>
          <input
            v-model.trim="draft.malware_family"
            placeholder="Ej. Lumma"
          />
        </label>

        <label class="field">
          <span>Fecha inicial</span>
          <input
            v-model="draft.date_from"
            type="date"
          />
        </label>

        <label class="field">
          <span>Fecha final</span>
          <input
            v-model="draft.date_to"
            type="date"
          />
        </label>

        <div class="filter-actions">
          <button
            type="submit"
            class="primary-button"
            :disabled="store.loading"
          >
            Aplicar filtros
          </button>

          <button
            type="button"
            class="secondary-button"
            :disabled="store.loading"
            @click="clearFilters"
          >
            Limpiar
          </button>
        </div>

      </form>
    </section>

    <section class="enterprise-panel results-panel">

      <div class="results-header">
        <div>
          <h2>Repositorio de IOC</h2>
          <p>
            Registros encontrados:
            <strong>
              {{ store.totalIOCs.toLocaleString("es-MX") }}
            </strong>
          </p>
        </div>
      </div>

      <ExplorerGrid
        :rows="store.items"
        :loading="store.loading"
        :error-message="store.errorMessage"
        @row-selected="store.selectIOC"
      />

      <footer class="pagination">
        <div>
          Página
          <strong>{{ store.currentPage }}</strong>
          de
          <strong>{{ store.totalPages }}</strong>
        </div>

        <div class="pagination-controls">
          <label>
            Registros

            <select
              :value="store.pagination.page_size"
              @change="store.setPageSize($event.target.value)"
            >
              <option :value="10">10</option>
              <option :value="25">25</option>
              <option :value="50">50</option>
              <option :value="100">100</option>
            </select>
          </label>

          <button
            type="button"
            :disabled="!store.hasPrevious || store.loading"
            @click="store.previousPage()"
          >
            Anterior
          </button>

          <button
            type="button"
            :disabled="!store.hasNext || store.loading"
            @click="store.nextPage()"
          >
            Siguiente
          </button>
        </div>
      </footer>

    </section>

    <aside
      v-if="store.selectedIOC"
      class="enterprise-panel selection-preview"
    >
      <div class="selection-heading">
        <h2>IOC seleccionado</h2>

        <button
          type="button"
          class="secondary-button"
          @click="store.clearSelection()"
        >
          Cerrar
        </button>
      </div>

      <div class="selection-details">
        <div>
          <span>Indicador</span>
          <strong>{{ store.selectedIOC.valor }}</strong>
        </div>

        <div>
          <span>Tipo</span>
          <strong>{{ store.selectedIOC.tipo || "—" }}</strong>
        </div>

        <div>
          <span>Estado VT</span>
          <strong>{{ store.selectedIOC.vt_estado || "—" }}</strong>
        </div>

        <div>
          <span>Score</span>
          <strong>{{ store.selectedIOC.vt_score ?? "—" }}</strong>
        </div>

        <div>
          <span>Fuente</span>
          <strong>{{ store.selectedIOC.fuente || "—" }}</strong>
        </div>
      </div>
    </aside>

  </section>
</template>

<script setup>
import { onMounted, reactive, watch } from "vue";
import { useRoute } from "vue-router";
import ExplorerGrid from "@/components/explorer/ExplorerGrid.vue";
import { useExplorerStore } from "@/stores/explorer.store";

const store = useExplorerStore();
const route = useRoute();

const emptyFilters = () => ({
  search: "",
  tipo: "",
  estado: "",
  country: "",
  fuente: "",
  campaign: "",
  malware_family: "",
  date_from: "",
  date_to: "",
});

const draft = reactive(emptyFilters());

function applyFilters() {
  store.filters = { ...draft };
  store.pagination.page = 1;
  store.clearSelection();
  store.loadIOCs();
}

function clearFilters() {
  Object.assign(draft, emptyFilters());
  applyFilters();
}

function syncRouteFilters() {
  const query = route.query;

  const hasFilters = [
    "search", "country", "tipo", "estado"
  ].some((key) => typeof query[key] === "string");

  if (!hasFilters) {
    if (!store.loaded) {
      store.loadIOCs();
    } else {
      Object.assign(draft, emptyFilters(), store.filters);
    }
    return;
  }

  const next = emptyFilters();

  for (const key of ["search", "country", "tipo", "estado"]) {
    if (typeof query[key] === "string") {
      next[key] = query[key];
    }
  }

  next.country = next.country.toUpperCase();

  Object.assign(draft, next);
  applyFilters();
}

onMounted(syncRouteFilters);

watch(
  () => route.fullPath,
  () => syncRouteFilters()
);

</script>

<style scoped>
.explorer {
  display: grid;
  gap: 22px;
  padding: 30px;
  color: #eef5fa;
}

.explorer-header,
.panel-heading,
.results-header,
.selection-heading {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 20px;
}

.explorer-header h1 {
  margin: 0;
  font-size: 30px;
  letter-spacing: -.03em;
}

.explorer-header p,
.panel-heading p,
.results-header p {
  margin: 8px 0 0;
  color: #8198aa;
  font-size: 13px;
}

.eyebrow {
  display: block;
  margin-bottom: 8px;
  color: #61adff;
  font-size: 11px;
  font-weight: 800;
  letter-spacing: .12em;
}

.enterprise-panel {
  min-width: 0;
  padding: 22px;
  border: 1px solid #1d3a50;
  border-radius: 13px;
  background: #0d1d2c;
}

.enterprise-panel h2 {
  margin: 0;
  font-size: 16px;
}

.filter-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16px;
  margin-top: 22px;
}

.field {
  display: grid;
  align-content: start;
  gap: 8px;
  min-width: 0;
}

.field-wide {
  grid-column: span 2;
}

.field span {
  color: #a4b9c8;
  font-size: 11px;
  font-weight: 700;
}

.field input,
.field select,
.pagination select {
  width: 100%;
  min-height: 41px;
  padding: 0 12px;
  border: 1px solid #27475e;
  border-radius: 8px;
  background: #081725;
  color: #eef5fa;
  font: inherit;
  font-size: 12px;
}

.field input:focus,
.field select:focus {
  outline: 2px solid #1683ff;
  outline-offset: 1px;
}

.filter-actions {
  display: flex;
  align-items: end;
  gap: 10px;
}

.primary-button,
.secondary-button,
.action-button,
.pagination button {
  min-height: 41px;
  padding: 0 15px;
  border-radius: 8px;
  color: #eef5fa;
  font-size: 12px;
  font-weight: 700;
  cursor: pointer;
}

.primary-button {
  border: 1px solid #1683ff;
  background: #126bc7;
}

.secondary-button,
.action-button,
.pagination button {
  border: 1px solid #31536b;
  background: #10283a;
}

.primary-button:hover {
  background: #1683ff;
}

.secondary-button:hover,
.action-button:hover,
.pagination button:hover {
  background: #1b3c53;
}

button:disabled {
  opacity: .45;
  cursor: not-allowed;
}

.results-header {
  margin-bottom: 18px;
}

.results-header strong {
  color: #eef5fa;
}

.pagination {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  margin-top: 18px;
  color: #8198aa;
  font-size: 12px;
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: 10px;
}

.pagination-controls label {
  display: flex;
  align-items: center;
  gap: 8px;
}

.pagination select {
  width: 78px;
}

.selection-preview {
  display: grid;
  gap: 20px;
}

.selection-details {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
}

.selection-details div {
  display: grid;
  gap: 7px;
  min-width: 0;
}

.selection-details span {
  color: #8198aa;
  font-size: 11px;
}

.selection-details strong {
  overflow-wrap: anywhere;
  font-size: 12px;
}

@media (max-width: 1200px) {
  .filter-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 760px) {
  .explorer {
    padding: 18px;
  }

  .explorer-header,
  .pagination {
    flex-direction: column;
    align-items: stretch;
  }

  .filter-grid,
  .selection-details {
    grid-template-columns: 1fr;
  }

  .field-wide {
    grid-column: auto;
  }

  .filter-actions,
  .pagination-controls {
    flex-wrap: wrap;
  }
}
</style>
