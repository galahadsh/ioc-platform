<template>
  <section class="dashboard">
    <header class="dashboard-header">
      <div>
        <span class="eyebrow">
          OVERVIEW
        </span>

        <h1>
          Dashboard
        </h1>

        <p>
          Resumen operativo del repositorio de indicadores
          y del estado general de la plataforma.
        </p>
      </div>

      <button
        type="button"
        class="refresh-button"
        :disabled="store.loading"
        @click="store.loadDashboard"
      >
        {{ store.loading ? "Actualizando..." : "Actualizar" }}
      </button>
    </header>

    <div
      v-if="store.loading && !store.loaded"
      class="state-panel"
    >
      Cargando dashboard...
    </div>

    <div
      v-else-if="store.error && !store.loaded"
      class="state-panel error"
    >
      <strong>
        No fue posible cargar la información.
      </strong>

      <span>
        {{ store.errorMessage }}
      </span>

      <button
        type="button"
        @click="store.loadDashboard"
      >
        Reintentar
      </button>
    </div>

    <template v-else>
      <div class="metrics-grid">
        <MetricCard
          title="IOC totales"
          :value="store.summary.total"
          trend="Repositorio consolidado"
          icon="◎"
          color="blue"
        />

        <MetricCard
          title="Maliciosos"
          :value="store.summary.maliciosos"
          :trend="maliciousPercentage"
          icon="!"
          color="red"
        />

        <MetricCard
          title="Sospechosos"
          :value="store.summary.sospechosos"
          trend="Requieren revisión"
          icon="?"
          color="orange"
        />

        <MetricCard
          title="Errores"
          :value="store.summary.errores"
          trend="Enriquecimientos con error"
          icon="×"
          color="red"
        />
      </div>

      <section class="health-panel">
        <div>
          <span class="eyebrow">
            PLATFORM STATUS
          </span>

          <h2>
            Estado de la plataforma
          </h2>
        </div>

        <div class="health-content">
          <span
            class="health-dot"
            :class="healthClass"
          ></span>

          <div>
            <strong>
              {{ healthLabel }}
            </strong>

            <p>
              {{ healthDescription }}
            </p>
          </div>
        </div>
      </section>
    </template>
  </section>
</template>

<script setup>
import {
  computed,
  onMounted,
} from "vue";

import MetricCard from
  "@/components/common/MetricCard.vue";

import {
  useDashboardStore,
} from "@/stores/dashboard.store";

const store = useDashboardStore();

const maliciousPercentage = computed(() => {
  const total = Number(
    store.summary.total || 0,
  );

  const malicious = Number(
    store.summary.maliciosos || 0,
  );

  if (!total) {
    return "0% del total";
  }

  const percentage = (
    (malicious / total) *
    100
  ).toFixed(1);

  return `${percentage}% del total`;
});

const normalizedHealth = computed(() => {
  const health = store.health;

  if (!health) {
    return "unknown";
  }

  if (typeof health === "string") {
    return health.toLowerCase();
  }

  return String(
    health.status ??
    health.state ??
    health.health ??
    "ok",
  ).toLowerCase();
});

const healthClass = computed(() => {
  if (
    normalizedHealth.value === "ok" ||
    normalizedHealth.value === "healthy" ||
    normalizedHealth.value === "available"
  ) {
    return "success";
  }

  if (
    normalizedHealth.value === "warning" ||
    normalizedHealth.value === "degraded"
  ) {
    return "warning";
  }

  return store.health
    ? "danger"
    : "unknown";
});

const healthLabel = computed(() => {
  if (healthClass.value === "success") {
    return "Servicios disponibles";
  }

  if (healthClass.value === "warning") {
    return "Servicio degradado";
  }

  if (healthClass.value === "danger") {
    return "Servicio no disponible";
  }

  return "Estado no disponible";
});

const healthDescription = computed(() => {
  if (store.health?.message) {
    return store.health.message;
  }

  if (healthClass.value === "success") {
    return "La API respondió correctamente.";
  }

  if (healthClass.value === "warning") {
    return "La plataforma reporta una condición que requiere revisión.";
  }

  if (healthClass.value === "danger") {
    return "No fue posible validar el estado de todos los servicios.";
  }

  return "Aún no se ha recibido información del endpoint de salud.";
});

onMounted(() => {
  store.loadDashboard();
});
</script>

<style scoped>
.dashboard {
  padding: 30px;
  color: #f8fafc;
}

.dashboard-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 24px;
  margin-bottom: 26px;
}

.dashboard-header h1 {
  margin: 0;
  font-size: 30px;
  letter-spacing: -0.03em;
}

.dashboard-header p {
  max-width: 720px;
  margin: 8px 0 0;
  color: #8ca0b3;
  line-height: 1.55;
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
.state-panel button {
  min-height: 40px;
  padding: 0 16px;
  border: 1px solid #31506b;
  border-radius: 9px;
  background: #14283a;
  color: #e2e8f0;
  cursor: pointer;
}

.refresh-button:disabled {
  cursor: wait;
  opacity: 0.65;
}

.metrics-grid {
  display: grid;
  grid-template-columns:
    repeat(4, minmax(180px, 1fr));
  gap: 18px;
}

.state-panel,
.health-panel {
  border: 1px solid #223449;
  border-radius: 14px;
  background: #162131;
}

.state-panel {
  display: grid;
  gap: 12px;
  justify-items: start;
  padding: 24px;
  color: #cbd5e1;
}

.state-panel.error {
  border-color: rgba(239, 68, 68, 0.45);
}

.state-panel span {
  color: #94a3b8;
}

.health-panel {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
  margin-top: 24px;
  padding: 22px;
}

.health-panel h2 {
  margin: 0;
  font-size: 18px;
}

.health-content {
  display: flex;
  align-items: center;
  gap: 13px;
  min-width: 290px;
  padding: 14px;
  border: 1px solid #263d52;
  border-radius: 11px;
  background: #0e1b29;
}

.health-content strong {
  display: block;
}

.health-content p {
  margin: 4px 0 0;
  color: #8ca0b3;
  font-size: 12px;
}

.health-dot {
  flex: 0 0 auto;
  width: 11px;
  height: 11px;
  border-radius: 50%;
}

.health-dot.success {
  background: #22c55e;
  box-shadow:
    0 0 12px rgba(34, 197, 94, 0.55);
}

.health-dot.warning {
  background: #f59e0b;
  box-shadow:
    0 0 12px rgba(245, 158, 11, 0.55);
}

.health-dot.danger {
  background: #ef4444;
  box-shadow:
    0 0 12px rgba(239, 68, 68, 0.55);
}

.health-dot.unknown {
  background: #64748b;
}

@media (max-width: 1100px) {
  .metrics-grid {
    grid-template-columns:
      repeat(2, minmax(180px, 1fr));
  }
}

@media (max-width: 720px) {
  .dashboard {
    padding: 20px;
  }

  .dashboard-header,
  .health-panel {
    align-items: stretch;
    flex-direction: column;
  }

  .metrics-grid {
    grid-template-columns: 1fr;
  }

  .health-content {
    min-width: 0;
  }
}
</style>
