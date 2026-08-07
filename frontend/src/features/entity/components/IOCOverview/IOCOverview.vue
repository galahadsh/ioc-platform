<template>
  <div class="ioc-overview">
    <EntityHeader
      type="IOC"
      :title="ioc.valor"
      :subtitle="ioc.tipo"
      :status="ioc.vt_estado"
      :provider="ioc.proveedor_reputacion"
    />

    <UiTabs aria-label="Detalle del IOC">
      <UiTab
        id="overview"
        label="Overview"
      >
        <EntitySection title="Información general">
          <EntityField
            label="ID"
            :value="ioc.id"
          />

          <EntityField
            label="Tipo"
            :value="ioc.tipo"
          />

          <EntityField
            label="Fuente"
            :value="ioc.fuente"
          />

          <EntityField
            label="Proveedor"
            :value="ioc.proveedor_reputacion"
          />

          <EntityField
            label="Campaña"
            :value="ioc.campaign"
          />

          <EntityField
            label="Malware"
            :value="ioc.malware_family"
          />

          <EntityField
            label="Fecha de creación"
            :value="formatDate(ioc.fecha_creacion)"
          />

          <EntityField
            label="Última consulta"
            :value="formatDate(ioc.ultima_consulta)"
          />
        </EntitySection>
      </UiTab>

      <UiTab
        id="virustotal"
        label="VirusTotal"
      >
        <VirusTotalCard
          :data="ioc"
        />
      </UiTab>

      <UiTab
        id="timeline"
        label="Timeline"
      >
        <EntitySection title="Línea de tiempo">
          <EntityField
            label="Creado"
            :value="formatDate(ioc.fecha_creacion)"
          />

          <EntityField
            label="Última consulta"
            :value="formatDate(ioc.ultima_consulta)"
          />

          <EntityField
            label="Estado VT"
            :value="ioc.vt_estado"
          />

          <EntityField
            label="Proveedor"
            :value="ioc.proveedor_reputacion"
          />
        </EntitySection>
      </UiTab>

      <UiTab
        id="raw-json"
        label="Raw JSON"
      >
        <EntitySection title="Respuesta del backend">
          <pre class="raw-json">{{ formattedJson }}</pre>
        </EntitySection>
      </UiTab>
    </UiTabs>
  </div>
</template>

<script setup>
import {
  computed,
} from "vue";

import EntityField from
  "../EntityField";

import EntityHeader from
  "../EntityHeader";

import EntitySection from
  "../EntitySection";

import VirusTotalCard from
  "../VirusTotalCard";

import {
  UiTab,
  UiTabs,
} from "@/shared/ui/Tabs";

const props = defineProps({
  ioc: {
    type: Object,
    required: true,
  },
});

const formattedJson = computed(() => {
  return JSON.stringify(
    props.ioc,
    null,
    2,
  );
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
      dateStyle: "medium",
      timeStyle: "short",
    },
  );
}
</script>

<style scoped>
.ioc-overview {
  display: flex;
  flex-direction: column;
  gap: 22px;
}

.raw-json {
  max-height: 460px;
  margin: 0;
  padding: 16px;
  overflow: auto;
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  background: #07111d;
  color: #cbd5e1;
  font-family:
    "Cascadia Code",
    "Fira Code",
    Consolas,
    monospace;
  font-size: 12px;
  line-height: 1.6;
  white-space: pre-wrap;
  overflow-wrap: anywhere;
}
</style>
