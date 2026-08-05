<template>
  <section class="grid-panel">
    <div
      v-if="loading"
      class="grid-state"
    >
      Cargando indicadores...
    </div>

    <div
      v-else-if="errorMessage"
      class="grid-state grid-state--error"
    >
      {{ errorMessage }}
    </div>

    <div
      v-else-if="!rows.length"
      class="grid-state"
    >
      No se encontraron IOC.
    </div>

    <AgGridVue
      v-else
      class="ioc-grid"
      :theme="gridTheme"
      :row-data="rows"
      :column-defs="columnDefs"
      :default-col-def="defaultColDef"
      :get-row-id="getRowId"
      :row-selection="rowSelection"
      animate-rows
      @row-clicked="handleRowClicked"
    />
  </section>
</template>

<script setup>
import {
  shallowRef,
} from "vue";

import {
  AgGridVue,
} from "ag-grid-vue3";

import {
  themeQuartz,
} from "ag-grid-community";

defineProps({
  rows: {
    type: Array,
    default: () => [],
  },

  loading: {
    type: Boolean,
    default: false,
  },

  errorMessage: {
    type: String,
    default: "",
  },
});

const emit = defineEmits([
  "row-selected",
]);

const rowSelection = {
  mode: "singleRow",
  enableClickSelection: true,
};

const gridTheme =
  themeQuartz.withParams({
    backgroundColor:
      "#111c2a",

    foregroundColor:
      "#dce7f0",

    headerBackgroundColor:
      "#0d1724",

    headerTextColor:
      "#8fa7b9",

    borderColor:
      "#26394b",

    rowHoverColor:
      "rgba(59, 130, 246, 0.10)",

    selectedRowBackgroundColor:
      "rgba(59, 130, 246, 0.18)",

    oddRowBackgroundColor:
      "rgba(255, 255, 255, 0.012)",

    fontFamily:
      "Inter, Segoe UI, Arial, sans-serif",

    fontSize: 12,
    headerFontSize: 11,
    headerFontWeight: 700,
    rowHeight: 48,
    headerHeight: 44,
    wrapperBorderRadius: 12,
  });

function formatDate(value) {
  if (!value) {
    return "—";
  }

  const date = new Date(value);

  if (
    Number.isNaN(
      date.getTime(),
    )
  ) {
    return String(value);
  }

  return date.toLocaleString(
    "es-MX",
    {
      dateStyle: "short",
      timeStyle: "short",
    },
  );
}

function formatStatus(params) {
  const status =
    String(
      params.value ??
      "pendiente",
    ).toLowerCase();

  const labels = {
    analizado: "Analizado",
    error: "Error",
    pendiente: "Pendiente",
  };

  return labels[status] ?? status;
}

const columnDefs = shallowRef([
  {
    field: "id",
    headerName: "ID",
    width: 90,
    pinned: "left",
  },
  {
    field: "tipo",
    headerName: "Tipo",
    width: 110,
  },
  {
    field: "valor",
    headerName: "IOC",
    minWidth: 310,
    flex: 1,
    tooltipField: "valor",
  },
  {
    field: "vt_estado",
    headerName: "Estado",
    width: 125,
    valueFormatter:
      formatStatus,

    cellClassRules: {
      "status-analyzed":
        (params) =>
          params.value ===
          "analizado",

      "status-error":
        (params) =>
          params.value ===
          "error",

      "status-pending":
        (params) =>
          params.value ===
          "pendiente",
    },
  },
  {
    field: "vt_score",
    headerName: "Score",
    width: 100,
    type: "numericColumn",
  },
  {
    field: "vt_malicious",
    headerName: "Malicious",
    width: 120,
    type: "numericColumn",
  },
  {
    field: "campaign",
    headerName: "Campaña",
    minWidth: 175,
  },
  {
    field: "malware_family",
    headerName: "Malware",
    minWidth: 150,
  },
  {
    field: "fuente",
    headerName: "Fuente",
    minWidth: 170,
  },
  {
    field: "ultima_consulta",
    headerName: "Última consulta",
    minWidth: 180,
    valueFormatter:
      (params) =>
        formatDate(
          params.value,
        ),
  },
]);

const defaultColDef = {
  sortable: true,
  resizable: true,
  filter: false,
};

function getRowId(params) {
  return String(
    params.data.id,
  );
}

function handleRowClicked(event) {
  emit(
    "row-selected",
    event.data,
  );
}
</script>

<style scoped>
.grid-panel {
  position: relative;
  min-height: 570px;
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  background: #111c2a;
  overflow: hidden;
}

.ioc-grid {
  width: 100%;
  height: 570px;
}

.grid-state {
  display: grid;
  place-items: center;
  min-height: 570px;
  color: var(--text-muted);
}

.grid-state--error {
  color: var(--danger);
}

:deep(.status-analyzed) {
  color: var(--success);
  font-weight: 700;
}

:deep(.status-error) {
  color: var(--danger);
  font-weight: 700;
}

:deep(.status-pending) {
  color: var(--warning);
  font-weight: 700;
}
</style>
