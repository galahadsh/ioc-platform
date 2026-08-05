<template>
  <section class="explorer">
    <header class="explorer-header">
      <div>
        <span class="eyebrow">
          IOC MANAGEMENT
        </span>

        <h1>
          IOC Explorer
        </h1>

        <p>
          Consulta y navega los indicadores almacenados
          en el repositorio central.
        </p>
      </div>

      <button
        type="button"
        class="refresh-button"
        :disabled="store.loading"
        @click="store.refresh"
      >
        {{
          store.loading
            ? "Actualizando..."
            : "Actualizar"
        }}
      </button>
    </header>

    <div class="explorer-summary">
      <span>
        Registros encontrados
      </span>

      <strong>
        {{
          store.totalIOCs
            .toLocaleString(
              "es-MX"
            )
        }}
      </strong>
    </div>

    <ExplorerGrid
      :rows="store.items"
      :loading="store.loading"
      :error-message="
        store.errorMessage
      "
      @row-selected="
        store.selectIOC
      "
    />

    <footer class="pagination">
      <div>
        Página
        <strong>
          {{ store.currentPage }}
        </strong>
        de
        <strong>
          {{ store.totalPages }}
        </strong>
      </div>

      <div class="pagination-controls">
        <label>
          Registros

          <select
            :value="
              store.pagination
                .page_size
            "
            @change="
              store.setPageSize(
                $event.target.value
              )
            "
          >
            <option :value="10">
              10
            </option>

            <option :value="25">
              25
            </option>

            <option :value="50">
              50
            </option>

            <option :value="100">
              100
            </option>
          </select>
        </label>

        <button
          type="button"
          :disabled="
            !store.hasPrevious ||
            store.loading
          "
          @click="
            store.previousPage
          "
        >
          Anterior
        </button>

        <button
          type="button"
          :disabled="
            !store.hasNext ||
            store.loading
          "
          @click="
            store.nextPage
          "
        >
          Siguiente
        </button>
      </div>
    </footer>

    <aside
      v-if="store.selectedIOC"
      class="selection-preview"
    >
      <span>
        IOC seleccionado
      </span>

      <strong>
        {{
          store.selectedIOC.valor
        }}
      </strong>

      <small>
        El panel de detalle se agregará
        en el siguiente PR.
      </small>
    </aside>
  </section>
</template>

<script setup>
import {
  onMounted,
} from "vue";

import ExplorerGrid from
  "@/components/explorer/ExplorerGrid.vue";

import {
  useExplorerStore,
} from "@/stores/explorer.store";

const store =
  useExplorerStore();

onMounted(() => {
  if (!store.loaded) {
    store.loadIOCs();
  }
});
</script>

<style scoped>
.explorer {
  padding: 30px;
  color: #f8fafc;
}

.explorer-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 24px;
  margin-bottom: 20px;
}

.explorer-header h1 {
  margin: 0;
  font-size: 30px;
  letter-spacing: -0.03em;
}

.explorer-header p {
  margin: 8px 0 0;
  color: #8ca0b3;
}

.eyebrow {
  display: block;
  margin-bottom: 7px;
  color: #60a5fa;
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 0.12em;
}

.refresh-button,
.pagination button,
.pagination select {
  min-height: 40px;
  border: 1px solid #31506b;
  border-radius: 9px;
  background: #14283a;
  color: #e2e8f0;
}

.refresh-button,
.pagination button {
  padding: 0 16px;
  cursor: pointer;
}

.pagination button:disabled,
.refresh-button:disabled {
  cursor: not-allowed;
  opacity: 0.45;
}

.explorer-summary {
  display: flex;
  align-items: baseline;
  gap: 10px;
  margin-bottom: 14px;
  color: #8ca0b3;
}

.explorer-summary strong {
  color: #f8fafc;
  font-size: 20px;
}

.pagination {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  margin-top: 16px;
  color: #8ca0b3;
  font-size: 13px;
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: 10px;
}

.pagination label {
  display: flex;
  align-items: center;
  gap: 8px;
}

.pagination select {
  padding: 0 10px;
}

.selection-preview {
  display: grid;
  gap: 5px;
  margin-top: 18px;
  padding: 16px;
  border: 1px solid #294359;
  border-radius: 11px;
  background: #132232;
}

.selection-preview span,
.selection-preview small {
  color: #8ca0b3;
}

.selection-preview strong {
  overflow-wrap: anywhere;
}

@media (max-width: 760px) {
  .explorer {
    padding: 20px;
  }

  .explorer-header,
  .pagination {
    align-items: stretch;
    flex-direction: column;
  }

  .pagination-controls {
    flex-wrap: wrap;
  }
}
</style>
