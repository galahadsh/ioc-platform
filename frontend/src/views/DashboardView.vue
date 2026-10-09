<template>
  <section class="executive-dashboard">
    <header class="page-header">
      <div>
        <span class="eyebrow">EXECUTIVE THREAT OVERVIEW</span>
        <h1>Panorama de Ciberamenazas</h1>
        <p>Indicadores estratégicos del repositorio de inteligencia.</p>
      </div>

      <div class="header-actions">
        <button
          class="button secondary"
          :disabled="store.loading"
          @click="store.loadDashboard()"
        >
          {{ store.loading ? "Actualizando..." : "↻ Actualizar" }}
        </button>

        <RouterLink to="/explorer" class="button primary">
          Explorar IOC →
        </RouterLink>
      </div>
    </header>

    <div v-if="store.errorMessage" class="error-banner" role="alert">
      No se pudieron consultar las estadísticas:
      {{ store.errorMessage }}
    </div>

    <div v-if="store.loading && !store.loaded" class="loading-banner">
      Consultando estadísticas del repositorio...
    </div>

    <template v-if="store.loaded">
      <div class="metrics">
        <article class="metric">
          <div class="metric-top">
            <span>IOC REGISTRADOS</span>
            <span class="metric-symbol blue">◎</span>
          </div>
          <strong>{{ number(summary.total) }}</strong>
          <small>Repositorio consolidado</small>
        </article>

        <article class="metric danger">
          <div class="metric-top">
            <span>IOC MALICIOSOS</span>
            <span class="metric-symbol red">!</span>
          </div>
          <strong>{{ number(summary.maliciosos) }}</strong>
          <small>{{ percentage(summary.maliciosos, summary.total) }} del total</small>
        </article>

        <article class="metric success">
          <div class="metric-top">
            <span>IOC ANALIZADOS</span>
            <span class="metric-symbol green">✓</span>
          </div>
          <strong>{{ number(analyzed) }}</strong>
          <small>{{ percentage(analyzed, summary.total) }} de cobertura</small>
        </article>

        <article class="metric warning">
          <div class="metric-top">
            <span>PENDIENTES</span>
            <span class="metric-symbol amber">◷</span>
          </div>
          <strong>{{ number(summary.pendientes) }}</strong>
          <small>Pendientes de enriquecimiento</small>
        </article>
      </div>

      <div class="insight-strip">
        <div>
          <span>Lectura ejecutiva</span>
          <strong>
            {{ number(summary.maliciosos) }} indicadores maliciosos
            identificados en el repositorio
          </strong>
        </div>
        <div class="insight-extra">
          <span>Sospechosos</span>
          <strong>{{ number(summary.sospechosos) }}</strong>
        </div>
        <div class="insight-extra">
          <span>Errores de análisis</span>
          <strong>{{ number(summary.errores) }}</strong>
        </div>
      </div>

      <div class="visual-grid">
        <article class="panel geography">
          <div class="panel-heading">
            <div>
              <span class="eyebrow">INTELIGENCIA GEOGRÁFICA</span>
              <h2>Distribución de IP maliciosas</h2>
              <p>Concentración por país de origen de los indicadores</p>
            </div>
            <span class="panel-tag">GeoIP</span>
          </div>

          <div class="geo-toolbar">
            <div class="geo-filters">
              <button
                type="button"
                :class="{ active: store.geoClassification === 'malicious' }"
                :disabled="store.geoLoading"
                @click="store.loadGeoStats('malicious')"
              >
                Maliciosos
              </button>
              <button
                type="button"
                :class="{ active: store.geoClassification === 'all' }"
                :disabled="store.geoLoading"
                @click="store.loadGeoStats('all')"
              >
                Todos
              </button>
            </div>
            <strong>{{ number(store.geoTotal) }} IOC IP</strong>
          </div>

          <div v-if="store.geoError" class="geo-message">
            {{ store.geoError }}
          </div>

          <div v-if="mapError" class="geo-message">
            {{ mapError }}
          </div>

          <VChart
            v-if="mapReady && !mapError"
            class="chart geo-chart"
            :option="geoOption"
            autoresize
          />

          <p v-else-if="!mapError" class="empty">
            Cargando mapa geográfico...
          </p>

          <div v-if="store.geoCountries.length" class="geo-ranking">
            <div
              v-for="item in store.geoCountries.slice(0, 5)"
              :key="item.country"
              class="geo-rank-item"
            >
              <span>{{ item.country }}</span>
              <strong>{{ number(item.total) }}</strong>
            </div>
          </div>

          <div class="panel-note">
            La geolocalización de IOC no equivale a ataques
            confirmados contra la infraestructura.
          </div>
        </article>

        <article class="panel">
          <div class="panel-heading">
            <div>
              <span class="eyebrow">COMPOSICIÓN</span>
              <h2>Tipos de indicadores</h2>
              <p>Distribución del repositorio</p>
            </div>
          </div>

          <VChart
            v-if="hasData(store.byType)"
            class="chart"
            :option="typeOption"
            autoresize
          />
          <p v-else class="empty">Sin datos de clasificación.</p>
        </article>

        <article class="panel wide">
          <div class="panel-heading">
            <div>
              <span class="eyebrow">EVOLUCIÓN</span>
              <h2>Actividad de enriquecimiento</h2>
              <p>
                Indicadores agrupados por mes de última consulta
              </p>
            </div>
          </div>

          <VChart
            v-if="hasData(store.byMonth)"
            class="chart chart-wide"
            :option="trendOption"
            autoresize
          />
          <p v-else class="empty">Sin fechas de consulta disponibles.</p>
        </article>

        <article class="panel">
          <div class="panel-heading">
            <div>
              <span class="eyebrow">INTELIGENCIA</span>
              <h2>Principales fuentes</h2>
              <p>Volumen de IOC por proveedor</p>
            </div>
          </div>

          <VChart
            v-if="hasData(store.bySource)"
            class="chart"
            :option="sourceOption"
            autoresize
          />
          <p v-else class="empty">Sin fuentes registradas.</p>
        </article>

        <article class="panel">
          <div class="panel-heading">
            <div>
              <span class="eyebrow">CAMPAÑAS</span>
              <h2>Campañas identificadas</h2>
              <p>Indicadores asociados a campañas</p>
            </div>
          </div>

          <div v-if="campaigns.length" class="rank-list">
            <div
              v-for="(item, index) in campaigns"
              :key="item.label"
              class="rank-item"
            >
              <span class="rank-number">{{ index + 1 }}</span>
              <span class="rank-label" :title="item.label">
                {{ item.label }}
              </span>
              <strong>{{ number(item.total) }}</strong>
            </div>
          </div>
          <p v-else class="empty">Sin campañas identificadas.</p>
        </article>
      </div>

      <footer class="dashboard-footer">
        Fuente: repositorio IOC Platform ·
        Clasificación basada en resultados almacenados de enriquecimiento.
      </footer>
    </template>
  </section>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import VChart from "vue-echarts";
import { use, registerMap } from "echarts/core";
import { CanvasRenderer } from "echarts/renderers";
import {
  PieChart,
  BarChart,
  LineChart,
  MapChart,
} from "echarts/charts";
import {
  GridComponent,
  TooltipComponent,
  LegendComponent,
  VisualMapComponent,
} from "echarts/components";
import { useDashboardStore } from "@/stores/dashboard.store";

use([
  CanvasRenderer,
  PieChart,
  BarChart,
  LineChart,
  MapChart,
  GridComponent,
  TooltipComponent,
  LegendComponent,
  VisualMapComponent,
]);

const store = useDashboardStore();

const mapReady = ref(false);
const mapError = ref("");

const geoOption = computed(() => ({
  backgroundColor: "transparent",
  tooltip: {
    trigger: "item",
    backgroundColor: "#102638",
    borderColor: "#31536b",
    textStyle: { color: "#eef5fa" },
    formatter: (params) => {
      const count = Number(params.value);

      if (!Number.isFinite(count)) {
        return `${params.name}: sin IOC IP registrados`;
      }

      return `${params.name}: ${number(count)} IOC IP`;
    },
  },
  visualMap: {
    min: 0,
    max: Math.max(
      1,
      ...store.geoCountries.map((item) => Number(item.total || 0))
    ),
    left: 5,
    bottom: 5,
    calculable: true,
    textStyle: { color: "#8ca3b5", fontSize: 10 },
    inRange: {
      color: ["#17334c", "#1765a5", "#1683ff", "#ff5068"],
    },
  },
  series: [{
    type: "map",
    map: "ioc-world",
    roam: true,
    zoom: 1.1,
    scaleLimit: { min: 1, max: 8 },
    nameProperty: "name",
    itemStyle: {
      areaColor: "#122c42",
      borderColor: "#38536a",
      borderWidth: 0.5,
    },
    emphasis: {
      label: { show: true, color: "#eef5fa" },
      itemStyle: { areaColor: "#f4a621" },
    },
    select: { disabled: true },
    data: store.geoCountries.map((item) => ({
      name: item.country,
      value: Number(item.total || 0),
    })),
  }],
}));

async function loadWorldMap() {
  try {
    const response = await fetch("/maps/world.geojson");

    if (!response.ok) {
      throw new Error(`No se pudo cargar el mapa: HTTP ${response.status}`);
    }

    const geojson = await response.json();

    if (!Array.isArray(geojson.features) || !geojson.features.length) {
      throw new Error("El GeoJSON no contiene países.");
    }

    // ECharts utilizará el código ISO Alpha-2 como nombre de cada región.
    for (const feature of geojson.features) {
      const code = feature.properties?.["ISO3166-1-Alpha-2"];
      if (code) {
        feature.properties.name = code;
      }
    }

    registerMap("ioc-world", geojson);
    mapReady.value = true;
  } catch (error) {
    console.error("GeoIP map error:", error);
    mapError.value = error.message || "Error al cargar el mapa.";
  }
}


const summary = computed(() => store.summary);

const analyzed = computed(() =>
  Math.max(
    0,
    Number(summary.value.total || 0) -
    Number(summary.value.pendientes || 0) -
    Number(summary.value.errores || 0)
  )
);

const number = (value) =>
  Number(value || 0).toLocaleString("es-MX");

const percentage = (part, total) =>
  Number(total) > 0
    ? `${((Number(part || 0) / Number(total)) * 100).toFixed(1)}%`
    : "0%";

const hasData = (items) =>
  Array.isArray(items) &&
  items.some((item) => Number(item.total) > 0);

const chartText = "#8ca3b5";
const chartGrid = "#223b50";

const tooltip = {
  trigger: "item",
  backgroundColor: "#102638",
  borderColor: "#31536b",
  textStyle: { color: "#eef5fa" },
};

const typeOption = computed(() => ({
  backgroundColor: "transparent",
  tooltip,
  color: ["#1683ff", "#39d98a", "#f4a621", "#9b85ff", "#ff5068"],
  legend: {
    bottom: 0,
    textStyle: { color: chartText, fontSize: 11 },
  },
  series: [{
    type: "pie",
    radius: ["48%", "70%"],
    center: ["50%", "43%"],
    label: { show: false },
    emphasis: {
      label: { show: true, color: "#eef5fa" },
    },
    data: store.byType.map((item) => ({
      name: item.label,
      value: Number(item.total || 0),
    })),
  }],
}));

const trendOption = computed(() => ({
  backgroundColor: "transparent",
  tooltip: { ...tooltip, trigger: "axis" },
  grid: { left: 45, right: 20, top: 25, bottom: 45 },
  xAxis: {
    type: "category",
    data: store.byMonth.map((item) => item.label),
    axisLabel: { color: chartText },
    axisLine: { lineStyle: { color: chartGrid } },
  },
  yAxis: {
    type: "value",
    minInterval: 1,
    axisLabel: { color: chartText },
    splitLine: { lineStyle: { color: chartGrid } },
  },
  series: [{
    type: "line",
    smooth: true,
    symbolSize: 8,
    lineStyle: { width: 3, color: "#1683ff" },
    itemStyle: { color: "#1683ff" },
    areaStyle: { color: "rgba(22,131,255,.12)" },
    data: store.byMonth.map((item) => Number(item.total || 0)),
  }],
}));

const sourceOption = computed(() => {
  const items = [...store.bySource]
    .filter((item) => Number(item.total) > 0)
    .slice(0, 8)
    .reverse();

  return {
    backgroundColor: "transparent",
    tooltip: { ...tooltip, trigger: "axis" },
    grid: { left: 115, right: 35, top: 10, bottom: 25 },
    xAxis: {
      type: "value",
      minInterval: 1,
      axisLabel: { color: chartText },
      splitLine: { lineStyle: { color: chartGrid } },
    },
    yAxis: {
      type: "category",
      data: items.map((item) => item.label),
      axisLabel: {
        color: chartText,
        width: 100,
        overflow: "truncate",
      },
      axisLine: { lineStyle: { color: chartGrid } },
    },
    series: [{
      type: "bar",
      barMaxWidth: 19,
      itemStyle: {
        color: "#1683ff",
        borderRadius: [0, 5, 5, 0],
      },
      data: items.map((item) => Number(item.total || 0)),
    }],
  };
});

const campaigns = computed(() =>
  store.byCampaign
    .filter((item) =>
      item.label &&
      item.label !== "Sin campaña" &&
      Number(item.total) > 0
    )
    .slice(0, 6)
);

onMounted(() => {
  store.loadDashboard();
  store.loadGeoStats("malicious");
  loadWorldMap();
});
</script>

<style scoped>
.geo-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
  margin: 12px 0;
  color: #eef5fa;
  font-size: 12px;
}

.geo-filters {
  display: flex;
  gap: 6px;
}

.geo-filters button {
  padding: 8px 12px;
  border: 1px solid #31536b;
  border-radius: 7px;
  background: #102638;
  color: #8ca3b5;
  cursor: pointer;
  font-size: 11px;
}

.geo-filters button.active {
  background: #126bc7;
  border-color: #1683ff;
  color: #fff;
}

.geo-filters button:disabled {
  opacity: .55;
  cursor: wait;
}

.geo-chart {
  height: 350px;
  min-height: 350px;
}

.geo-ranking {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 7px;
  margin-top: 10px;
}

.geo-rank-item {
  display: flex;
  flex-direction: column;
  gap: 5px;
  padding: 9px;
  border: 1px solid #1d3a50;
  border-radius: 7px;
  background: #0a1a29;
  font-size: 11px;
}

.geo-rank-item span { color: #8ca3b5; }
.geo-rank-item strong { color: #eef5fa; }

.geo-message {
  padding: 10px;
  color: #ff7185;
  font-size: 12px;
}

@media (max-width: 760px) {
  .geo-ranking {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

.executive-dashboard {
  min-height: 100%;
  padding: 30px;
  background: #07111d;
  color: #eef5fa;
}

.page-header,
.header-actions,
.metric-top,
.panel-heading {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
}

.page-header { margin-bottom: 24px; }

.eyebrow {
  display: block;
  margin-bottom: 9px;
  color: #61adff;
  font-size: 10px;
  font-weight: 800;
  letter-spacing: .12em;
}

h1, h2, h3, p { margin-top: 0; }

h1 {
  margin-bottom: 8px;
  font-size: 29px;
  letter-spacing: -.035em;
}

.page-header p,
.panel-heading p,
.metric small,
.dashboard-footer {
  color: #8198aa;
  font-size: 12px;
}

.button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 40px;
  padding: 0 15px;
  border-radius: 8px;
  color: #eef5fa;
  text-decoration: none;
  font-size: 12px;
  font-weight: 700;
  cursor: pointer;
}

.button.primary {
  background: #126bc7;
  border: 1px solid #1683ff;
}

.button.secondary {
  background: #10283a;
  border: 1px solid #31536b;
}

button:disabled { opacity: .5; cursor: not-allowed; }

.metrics {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 15px;
  margin-bottom: 18px;
}

.metric,
.panel,
.insight-strip {
  min-width: 0;
  border: 1px solid #1d3a50;
  border-radius: 13px;
  background: linear-gradient(145deg, #0e2233, #0a1927);
}

.metric {
  min-height: 145px;
  padding: 20px;
}

.metric-top span:first-child {
  color: #8ca3b5;
  font-size: 10px;
  font-weight: 800;
  letter-spacing: .06em;
}

.metric-symbol {
  display: grid;
  place-items: center;
  width: 27px;
  height: 27px;
  border-radius: 8px;
  font-size: 17px;
  font-weight: 800;
}

.blue { color: #61adff; background: #102f4f; }
.red { color: #ff7185; background: #3c1e31; }
.green { color: #39d98a; background: #153b34; }
.amber { color: #f4a621; background: #3d3220; }

.metric strong {
  display: block;
  margin: 15px 0 8px;
  font-size: 32px;
  line-height: 1;
  letter-spacing: -.035em;
}

.metric.danger strong { color: #ff7185; }
.metric.success strong { color: #39d98a; }
.metric.warning strong { color: #f4a621; }

.insight-strip {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  padding: 18px 22px;
  margin-bottom: 18px;
}

.insight-strip > div {
  display: grid;
  gap: 7px;
}

.insight-strip span {
  color: #8198aa;
  font-size: 11px;
}

.insight-strip strong { font-size: 13px; }

.insight-extra {
  padding-left: 20px;
  border-left: 1px solid #1d3a50;
  white-space: nowrap;
}

.visual-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 18px;
}

.panel {
  padding: 22px;
}

.panel-heading h2 {
  margin-bottom: 7px;
  font-size: 17px;
}

.panel-tag {
  padding: 6px 10px;
  border: 1px solid #31536b;
  border-radius: 20px;
  color: #61adff;
  font-size: 10px;
}

.chart {
  width: 100%;
  height: 310px;
}

.chart-wide { height: 280px; }

.wide { grid-column: 1 / -1; }

.map-placeholder {
  display: flex;
  min-height: 275px;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 28px;
  border: 1px dashed #31536b;
  border-radius: 12px;
  background:
    radial-gradient(ellipse at center, #12334c 0%, #081725 72%);
  text-align: center;
}

.map-icon {
  color: #61adff;
  font-size: 44px;
}

.map-placeholder h3 {
  margin: 12px 0 8px;
  font-size: 16px;
}

.map-placeholder p {
  max-width: 390px;
  color: #8ca3b5;
  font-size: 12px;
  line-height: 1.7;
}

.map-link {
  color: #61adff;
  font-size: 12px;
  text-decoration: none;
}

.panel-note {
  margin-top: 13px;
  color: #8198aa;
  font-size: 10px;
}

.rank-list {
  display: grid;
  gap: 10px;
  margin-top: 24px;
}

.rank-item {
  display: grid;
  grid-template-columns: 26px minmax(0, 1fr) auto;
  align-items: center;
  gap: 12px;
  padding: 13px;
  border: 1px solid #1d3a50;
  border-radius: 8px;
  background: #0a1a29;
  font-size: 12px;
}

.rank-number { color: #61adff; }
.rank-label { overflow-wrap: anywhere; }
.rank-item strong { color: #eef5fa; }

.empty {
  padding: 45px 0;
  color: #8198aa;
  text-align: center;
  font-size: 12px;
}

.error-banner,
.loading-banner {
  padding: 14px;
  margin-bottom: 18px;
  border: 1px solid #31536b;
  border-radius: 9px;
  color: #d7e8f5;
}

.error-banner {
  border-color: #914052;
  color: #ff7185;
}

.dashboard-footer {
  margin-top: 24px;
  line-height: 1.6;
}

@media (max-width: 1100px) {
  .metrics { grid-template-columns: repeat(2, 1fr); }
}

@media (max-width: 760px) {
  .executive-dashboard { padding: 18px; }
  .page-header, .insight-strip {
    flex-direction: column;
    align-items: stretch;
  }
  .metrics, .visual-grid {
    grid-template-columns: 1fr;
  }
  .wide { grid-column: auto; }
  .header-actions { flex-wrap: wrap; }
  .insight-extra {
    padding-left: 0;
    border-left: 0;
  }
}
</style>
