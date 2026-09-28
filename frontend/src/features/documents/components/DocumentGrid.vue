<template>
  <UiCard
    title="Documentos"
    subtitle="Repositorio central de inteligencia."
  >
    <div
      v-if="loading"
      class="documents-state"
    >
      Cargando documentos...
    </div>

    <div
      v-else-if="!documents.length"
      class="documents-state"
    >
      No hay documentos registrados.
    </div>

    <div
      v-else
      class="documents-table-wrapper"
    >
      <table class="documents-table">
        <thead>
          <tr>
            <th>Documento</th>
            <th>Estado</th>
            <th>Fuente</th>
            <th>TLP</th>
            <th>Tamaño</th>
            <th>Fecha</th>
            <th />
          </tr>
        </thead>

        <tbody>
          <tr
            v-for="document in documents"
            :key="document.id"
          >
            <td>
              <div class="document-name">
                <strong>
                  {{
                    document.original_name
                  }}
                </strong>

                <small>
                  {{
                    document.extension
                      ?.toUpperCase() ||
                    "FILE"
                  }}
                </small>
              </div>
            </td>

            <td>
              <StatusBadge
                :status="
                  mapStatus(
                    document.status,
                  )
                "
              />
            </td>

            <td>
              {{ document.source || "—" }}
            </td>

            <td>
              {{ document.tlp || "—" }}
            </td>

            <td>
              {{
                formatBytes(
                  document.size_bytes,
                )
              }}
            </td>

            <td>
              {{
                formatDate(
                  document.uploaded_at,
                )
              }}
            </td>

            <td class="documents-table__actions">
              <UiButton
                variant="ghost"
                size="sm"
                @click="
                  $emit(
                    'download',
                    document,
                  )
                "
              >
                Descargar
              </UiButton>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </UiCard>
</template>

<script setup>
import UiButton from
  "@/shared/ui/Button";

import UiCard from
  "@/shared/ui/Card";

import StatusBadge from
  "@/shared/ui/StatusBadge";

defineProps({
  documents: {
    type: Array,
    default: () => [],
  },

  loading: {
    type: Boolean,
    default: false,
  },
});

defineEmits([
  "download",
]);

function mapStatus(status) {
  const map = {
    UPLOADED: "pending",
    QUEUED: "pending",
    PROCESSING: "pending",
    PROCESSED: "analizado",
    CORRELATED: "analizado",
    ERROR: "error",
    ARCHIVED: "unknown",
  };

  return (
    map[
      String(status).toUpperCase()
    ] ?? "unknown"
  );
}

function formatBytes(bytes) {
  if (!bytes) {
    return "0 B";
  }

  const units = [
    "B",
    "KB",
    "MB",
    "GB",
  ];

  let value = Number(bytes);
  let unit = 0;

  while (
    value >= 1024 &&
    unit < units.length - 1
  ) {
    value /= 1024;
    unit += 1;
  }

  return `${value.toFixed(
    unit === 0 ? 0 : 1,
  )} ${units[unit]}`;
}

function formatDate(value) {
  if (!value) {
    return "—";
  }

  return new Date(
    value,
  ).toLocaleString(
    "es-MX",
    {
      dateStyle: "short",
      timeStyle: "short",
    },
  );
}
</script>

<style scoped>
.documents-state {
  padding: 50px 20px;
  color: var(--text-muted);
  text-align: center;
}

.documents-table-wrapper {
  overflow-x: auto;
}

.documents-table {
  width: 100%;
  border-collapse: collapse;
}

.documents-table th,
.documents-table td {
  padding: 14px 12px;
  border-bottom: 1px solid var(--border);
  text-align: left;
}

.documents-table th {
  color: var(--text-muted);
  font-size: 11px;
  letter-spacing: 0.05em;
  text-transform: uppercase;
}

.documents-table td {
  color: var(--text);
  font-size: 13px;
}

.document-name {
  display: grid;
  gap: 3px;
}

.document-name small {
  color: var(--text-muted);
}

.documents-table__actions {
  text-align: right;
}
</style>
