<template>
  <section class="explorer">
    <header class="explorer__header">
      <div>
        <span class="explorer__eyebrow">
          IOC MANAGEMENT
        </span>

        <h1>
          IOC Explorer
        </h1>

        <p>
          Consulta y navega los indicadores
          almacenados en el repositorio central.
        </p>
      </div>

      <UiButton
        variant="secondary"
        :loading="store.loading"
        @click="store.refresh"
      >
        Actualizar
      </UiButton>
    </header>

    <div class="explorer__summary">
      <span>
        Registros encontrados
      </span>

      <strong>
        {{
          store.totalIOCs.toLocaleString(
            "es-MX",
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
        handleRowSelected
      "
    />

    <footer class="explorer__pagination">
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

      <div class="explorer__pagination-actions">
        <label>
          Registros

          <select
            :value="
              store.pagination.page_size
            "
            @change="
              store.setPageSize(
                $event.target.value,
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

        <UiButton
          variant="ghost"
          size="sm"
          :disabled="
            !store.hasPrevious ||
            store.loading
          "
          @click="
            store.previousPage
          "
        >
          Anterior
        </UiButton>

        <UiButton
          variant="ghost"
          size="sm"
          :disabled="
            !store.hasNext ||
            store.loading
          "
          @click="
            store.nextPage
          "
        >
          Siguiente
        </UiButton>
      </div>
    </footer>

    <UiDrawer
      v-model="store.drawerOpen"
      title="Detalle del IOC"
      subtitle="Información consolidada del indicador"
      :width="600"
      @close="store.closeDrawer"
    >
      <div
        v-if="store.detailLoading"
        class="drawer-state"
      >
        Cargando detalle del IOC...
      </div>

      <div
        v-else-if="
          store.detailErrorMessage
        "
        class="drawer-state drawer-state--error"
      >
        <strong>
          No fue posible cargar el IOC.
        </strong>

        <span>
          {{
            store.detailErrorMessage
          }}
        </span>
      </div>

      <IOCOverview
        v-else-if="store.selectedIOC"
        :ioc="store.selectedIOC"
      />

      <div
        v-else
        class="drawer-state"
      >
        Selecciona un IOC para consultar
        su información.
      </div>

      <template #footer>
        <div class="drawer-footer">
          <UiButton
            variant="ghost"
            @click="
              store.closeDrawer
            "
          >
            Cerrar
          </UiButton>
        </div>
      </template>
    </UiDrawer>
  </section>
</template>

<script setup>
import {
  onMounted,
} from "vue";

import ExplorerGrid from
  "@/features/explorer/components/ExplorerGrid.vue";

import {
  useExplorerStore,
} from "@/features/explorer/stores/explorer.store";

import IOCOverview from
  "@/features/entity/components/IOCOverview";

import UiButton from
  "@/shared/ui/Button";

import UiDrawer from
  "@/shared/ui/Drawer";

const store =
  useExplorerStore();

function handleRowSelected(ioc) {
  store.loadIOCDetail(ioc);
}

onMounted(() => {
  if (!store.loaded) {
    store.loadIOCs();
  }
});
</script>

<style scoped>
.explorer {
  padding: 30px;
  color: var(--text);
}

.explorer__header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 24px;
  margin-bottom: 20px;
}

.explorer__header h1 {
  margin: 0;
  font-size: 30px;
  letter-spacing: -0.03em;
}

.explorer__header p {
  margin: 8px 0 0;
  color: var(--text-muted);
}

.explorer__eyebrow {
  display: block;
  margin-bottom: 7px;
  color: var(--primary);
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 0.12em;
}

.explorer__summary {
  display: flex;
  align-items: baseline;
  gap: 10px;
  margin-bottom: 14px;
  color: var(--text-muted);
}

.explorer__summary strong {
  color: var(--text);
  font-size: 20px;
}

.explorer__pagination {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  margin-top: 16px;
  color: var(--text-muted);
  font-size: 13px;
}

.explorer__pagination-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.explorer__pagination label {
  display: flex;
  align-items: center;
  gap: 8px;
}

.explorer__pagination select {
  min-height: 36px;
  padding: 0 10px;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  background: var(--surface);
  color: var(--text);
}

.drawer-state {
  display: grid;
  gap: 9px;
  place-content: center;
  min-height: 300px;
  color: var(--text-muted);
  text-align: center;
}

.drawer-state--error {
  color: var(--danger);
}

.drawer-footer {
  display: flex;
  justify-content: flex-end;
}

@media (max-width: 760px) {
  .explorer {
    padding: 20px;
  }

  .explorer__header,
  .explorer__pagination {
    align-items: stretch;
    flex-direction: column;
  }

  .explorer__pagination-actions {
    flex-wrap: wrap;
  }
}
</style>
