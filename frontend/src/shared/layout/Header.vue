<template>
  <header class="enterprise-header">

    <div class="enterprise-header-title">
      <span class="enterprise-eyebrow">
        Cyber Threat Intelligence
      </span>
      <h1>{{ pageTitle }}</h1>
    </div>

    <div class="enterprise-header-actions">

      <form
        class="enterprise-search"
        role="search"
        @submit.prevent="searchIoc"
      >
        <span>⌕</span>
        <input
          v-model.trim="search"
          type="search"
          aria-label="Buscar IOC"
          placeholder="Buscar IOC..."
        />
      </form>

      <button
        type="button"
        class="enterprise-icon-button"
        title="Actualizar dashboard"
        aria-label="Actualizar dashboard"
        :disabled="dashboard.loading"
        @click="refresh"
      >
        ↻
      </button>

      <div class="enterprise-user">
        <div class="enterprise-avatar">
          {{ initials }}
        </div>

        <div>
          <strong>{{ displayName }}</strong>
          <span>{{ displayRole }}</span>
        </div>
      </div>

      <button
        type="button"
        class="logout-button"
        @click="logout"
      >
        Cerrar sesión
      </button>

    </div>
  </header>
</template>

<script setup>
import { computed, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useAuthStore } from "@/stores/auth.store";
import { useDashboardStore } from "@/stores/dashboard.store";

const router = useRouter();
const route = useRoute();
const auth = useAuthStore();
const dashboard = useDashboardStore();

const search = ref("");

const titles = {
  dashboard: "Dashboard",
  documents: "Document Center",
  explorer: "IOC Explorer",
  campaigns: "Campaigns",
  malware: "Malware",
  actors: "Threat Actors",
  cases: "Cases",
  reports: "Reports",
};

const pageTitle = computed(
  () => titles[route.name] ?? "IOC Platform Enterprise"
);

const displayName = computed(
  () => auth.user?.full_name || auth.user?.username || "Usuario"
);

const displayRole = computed(
  () => auth.user?.roles?.join(", ") || "Sin rol"
);

const initials = computed(() =>
  displayName.value
    .trim()
    .split(/\s+/)
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase() || "")
    .join("")
);

function logout() {
  auth.clearSession();
  router.replace("/login");
}

function refresh() {
  dashboard.loadDashboard();
}

function searchIoc() {
  if (!search.value) return;

  router.push({
    path: "/explorer",
    query: { search: search.value },
  });
}
</script>

<style scoped>
.enterprise-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
  min-height: 84px;
  padding: 16px 28px;
  border-bottom: 1px solid #1d3a50;
  background: rgba(7,19,31,.92);
  color: #eef5fa;
}

.enterprise-eyebrow {
  display: block;
  margin-bottom: 7px;
  color: #61adff;
  font-size: 10px;
  font-weight: 800;
  letter-spacing: .09em;
}

.enterprise-header h1 {
  margin: 0;
  font-size: 21px;
  letter-spacing: -.025em;
}

.enterprise-header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.enterprise-search {
  display: flex;
  align-items: center;
  gap: 9px;
  width: 310px;
  min-height: 39px;
  padding: 0 12px;
  border: 1px solid #1d3a50;
  border-radius: 9px;
  background: rgba(10,31,47,.72);
  color: #527990;
}

.enterprise-search input {
  width: 100%;
  border: 0;
  outline: 0;
  background: transparent;
  color: #eef5fa;
  font-size: 11px;
}

.enterprise-search input::placeholder {
  color: #587083;
}

.enterprise-icon-button {
  display: grid;
  place-items: center;
  width: 39px;
  height: 39px;
  border: 1px solid #1d3a50;
  border-radius: 9px;
  background: rgba(12,35,52,.75);
  color: #9ab0bf;
  cursor: pointer;
}

.enterprise-icon-button:hover {
  background: #163249;
}

.enterprise-user {
  display: flex;
  align-items: center;
  gap: 9px;
  padding-left: 3px;
}

.enterprise-avatar {
  display: grid;
  place-items: center;
  width: 37px;
  height: 37px;
  flex-shrink: 0;
  border-radius: 50%;
  background: rgba(22,131,255,.13);
  color: #65b1ff;
  font-size: 11px;
  font-weight: 850;
}

.enterprise-user strong,
.enterprise-user span {
  display: block;
}

.enterprise-user strong {
  font-size: 11px;
}

.enterprise-user span {
  margin-top: 3px;
  color: #8198aa;
  font-size: 10px;
}

.logout-button {
  min-height: 38px;
  padding: 0 12px;
  border: 1px solid #31536b;
  border-radius: 8px;
  background: #10283a;
  color: #eef5fa;
  font-size: 11px;
  cursor: pointer;
}

.logout-button:hover {
  background: #1d3e56;
}

button:focus-visible,
input:focus-visible {
  outline: 2px solid #61adff;
  outline-offset: 2px;
}

@media (max-width: 1150px) {
  .enterprise-header {
    flex-wrap: wrap;
  }

  .enterprise-header-actions {
    flex-wrap: wrap;
  }

  .enterprise-search {
    width: min(310px, 100%);
  }
}

@media (max-width: 760px) {
  .enterprise-header {
    padding: 18px;
  }

  .enterprise-header-actions {
    width: 100%;
  }

  .enterprise-search {
    flex: 1;
    min-width: 180px;
  }
}
</style>
