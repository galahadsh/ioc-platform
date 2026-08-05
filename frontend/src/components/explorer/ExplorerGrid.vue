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
      class="grid-state error"
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
      row-selection="single"
      animate-rows
      @row-clicked="onRowClicked"
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

const props = defineProps({
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

    fontSize:
      12,

    headerFontSize:
      11,

    headerFontWeight:
      700,

    rowHeight:
      48,

    headerHeight:
      44,

    wrapperBorderRadius:
      12,
  });

function formatDate(value) {
  if (!value) {
    return "—";
  }

  const date = new Date(value);

  if (
    Number.isNaN(
      date.getTime()
    )
  ) {
    return value;
  }

  return date.toLocaleString(
    "es-MX",
    {
      dateStyle: "short",
      timeStyle: "short",
    }
  );
}

function statusLabel(params) {
  const status =
    params.value ?? "pendiente";

  const labels = {
    analizado: "Analizado",
    error: "Error",
    pendiente: "Pendiente",
  };

  return (
    labels[status] ??
    status
  );
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
    minWidth: 320,
    flex: 1,
    tooltipField: "valor",
  },
  {
    field: "vt_estado",
    headerName: "Estado",
    width: 125,
    valueFormatter:
      statusLabel,

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
    width: 105,
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
          params.value
        ),
  },
]);

const defaultColDef = {
  sortable: true,
  resizable: true,
  filter: false,
  suppressMovable: false,
};

function getRowId(params) {
  return String(
    params.data.id
  );
}

function onRowClicked(event) {
  emit(
    "row-selected",
    event.data
  );
}
</script>

<style scoped>
.grid-panel {
  position: relative;
  min-height: 570px;
  border: 1px solid #26394b;
  border-radius: 13px;
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
  color: #91a6b6;
}

.grid-state.error {
  color: #f87171;
}

:deep(.status-analyzed) {
  color: #4ade80;
  font-weight: 700;
}

:deep(.status-error) {
  color: #fb7185;
  font-weight: 700;
}

:deep(.status-pending) {
  color: #fbbf24;
  font-weight: 700;
}
</style>
