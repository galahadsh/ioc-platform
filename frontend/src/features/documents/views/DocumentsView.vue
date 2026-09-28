<template>
  <section class="documents-view">
    <header class="documents-view__header">
      <div>
        <span class="documents-view__eyebrow">
          INGESTA
        </span>

        <h1>
          Document Center
        </h1>

        <p>
          Almacena, procesa y consulta
          documentos de inteligencia.
        </p>
      </div>

      <UiButton
        variant="secondary"
        :loading="store.loading"
        @click="store.loadDocuments"
      >
        Actualizar
      </UiButton>
    </header>

    <div
      v-if="store.errorMessage"
      class="documents-alert documents-alert--error"
    >
      {{ store.errorMessage }}
    </div>

    <div
      v-if="store.uploadMessage"
      class="documents-alert"
    >
      {{ store.uploadMessage }}
    </div>

    <DocumentUpload />

    <DocumentGrid
      :documents="store.items"
      :loading="store.loading"
      @download="
        store.downloadDocument
      "
    />

    <footer class="documents-pagination">
      <span>
        Página
        {{ store.pagination.page }}
        de
        {{ store.pagination.pages || 1 }}

        ·

        {{
          store.totalDocuments
        }}
        documentos
      </span>

      <div>
        <UiButton
          variant="ghost"
          size="sm"
          :disabled="
            !store.hasPrevious
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
            !store.hasNext
          "
          @click="
            store.nextPage
          "
        >
          Siguiente
        </UiButton>
      </div>
    </footer>
  </section>
</template>

<script setup>
import {
  onMounted,
} from "vue";

import DocumentGrid from
  "@/features/documents/components/DocumentGrid.vue";

import DocumentUpload from
  "@/features/documents/components/DocumentUpload.vue";

import {
  useDocumentsStore,
} from "@/features/documents/stores/documents.store";

import UiButton from
  "@/shared/ui/Button";

const store =
  useDocumentsStore();

onMounted(() => {
  store.loadDocuments();
});
</script>

<style scoped>
.documents-view {
  display: grid;
  gap: 22px;
  padding: 30px;
}

.documents-view__header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 20px;
}

.documents-view__header h1 {
  margin: 0;
  color: var(--text);
  font-size: 30px;
}

.documents-view__header p {
  margin: 7px 0 0;
  color: var(--text-muted);
}

.documents-view__eyebrow {
  display: block;
  margin-bottom: 7px;
  color: var(--primary);
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 0.12em;
}

.documents-alert {
  padding: 13px 16px;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  background: var(--surface);
  color: var(--success);
}

.documents-alert--error {
  color: var(--danger);
}

.documents-pagination {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 15px;
  color: var(--text-muted);
  font-size: 13px;
}

.documents-pagination > div {
  display: flex;
  gap: 8px;
}

@media (max-width: 760px) {
  .documents-view {
    padding: 20px;
  }

  .documents-view__header,
  .documents-pagination {
    align-items: stretch;
    flex-direction: column;
  }
}
</style>
