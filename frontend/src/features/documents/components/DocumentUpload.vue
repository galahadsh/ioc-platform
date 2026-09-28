<template>
  <UiCard
    title="Upload Intelligence"
    subtitle="Carga documentos para almacenamiento y procesamiento."
  >
    <form
      class="document-upload"
      @submit.prevent="submit"
    >
      <label class="upload-dropzone">
        <input
          type="file"
          class="upload-dropzone__input"
          @change="selectFile"
        />

        <strong>
          {{
            file
              ? file.name
              : "Seleccionar documento"
          }}
        </strong>

        <span>
          PDF, CSV, XLSX, DOCX, JSON,
          TXT y otros formatos.
        </span>
      </label>

      <div class="document-upload__fields">
        <label>
          Fuente

          <select v-model="source">
            <option value="INTERNAL">
              Interno
            </option>

            <option value="INTEL471">
              Intel471
            </option>

            <option value="SOCRADAR">
              SOCradar
            </option>

            <option value="CISA">
              CISA
            </option>

            <option value="OTHER">
              Otro
            </option>
          </select>
        </label>

        <label>
          TLP

          <select v-model="tlp">
            <option value="TLP:CLEAR">
              TLP:CLEAR
            </option>

            <option value="TLP:GREEN">
              TLP:GREEN
            </option>

            <option value="TLP:AMBER">
              TLP:AMBER
            </option>

            <option value="TLP:RED">
              TLP:RED
            </option>
          </select>
        </label>

        <label>
          Clasificación

          <input
            v-model="classification"
            type="text"
            placeholder="Ej. Ransomware"
          />
        </label>
      </div>

      <div class="document-upload__actions">
        <UiButton
          type="submit"
          :loading="store.uploading"
          :disabled="!file"
        >
          Subir documento
        </UiButton>
      </div>
    </form>
  </UiCard>
</template>

<script setup>
import {
  ref,
} from "vue";

import UiButton from
  "@/shared/ui/Button";

import UiCard from
  "@/shared/ui/Card";

import {
  useDocumentsStore,
} from "@/features/documents/stores/documents.store";

const store =
  useDocumentsStore();

const file = ref(null);

const source =
  ref("INTERNAL");

const tlp =
  ref("TLP:CLEAR");

const classification =
  ref("");

function selectFile(event) {
  file.value =
    event.target.files?.[0] ??
    null;
}

async function submit() {
  if (!file.value) {
    return;
  }

  await store.uploadDocument({
    file: file.value,
    source: source.value,
    tlp: tlp.value,
    classification:
      classification.value,
    uploadedBy: "maverick",
  });

  file.value = null;
  classification.value = "";
}
</script>

<style scoped>
.document-upload {
  display: grid;
  gap: 20px;
}

.upload-dropzone {
  display: grid;
  place-items: center;
  gap: 8px;
  min-height: 170px;
  padding: 24px;
  border: 1px dashed var(--border);
  border-radius: var(--radius-md);
  background: rgba(255, 255, 255, 0.015);
  color: var(--text);
  cursor: pointer;
}

.upload-dropzone:hover {
  border-color: var(--primary);
}

.upload-dropzone__input {
  display: none;
}

.upload-dropzone span {
  color: var(--text-muted);
  font-size: 13px;
}

.document-upload__fields {
  display: grid;
  grid-template-columns:
    repeat(3, minmax(0, 1fr));
  gap: 14px;
}

.document-upload__fields label {
  display: grid;
  gap: 7px;
  color: var(--text-muted);
  font-size: 12px;
  font-weight: 700;
}

.document-upload__fields input,
.document-upload__fields select {
  min-height: 42px;
  padding: 0 12px;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  background: var(--background);
  color: var(--text);
}

.document-upload__actions {
  display: flex;
  justify-content: flex-end;
}

@media (max-width: 850px) {
  .document-upload__fields {
    grid-template-columns: 1fr;
  }
}
</style>
