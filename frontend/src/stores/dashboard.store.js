import {
  defineStore,
} from "pinia";

import DashboardApi from
  "@/api/dashboard.api";

const emptySummary = () => ({
  total: 0,
  maliciosos: 0,
  sospechosos: 0,
  limpios: 0,
  pendientes: 0,
  errores: 0,
});

export const useDashboardStore =
  defineStore(
    "dashboard",
    {
      state: () => ({
        loading: false,
        loaded: false,
        error: null,
        errorMessage: "",
        summary: emptySummary(),
        byType: [],
        bySource: [],
        byCampaign: [],
        byMalware: [],
        byMonth: [],
        health: null,
      }),

      actions: {
        async loadDashboard() {
          if (this.loading) {
            return;
          }

          this.loading = true;
          this.error = null;
          this.errorMessage = "";

          try {
            const [
              statsResult,
              healthResult,
            ] = await Promise.allSettled([
              DashboardApi.getStats(),
              DashboardApi.getHealth(),
            ]);

            if (
              statsResult.status ===
              "rejected"
            ) {
              throw statsResult.reason;
            }

            const stats =
              statsResult.value ?? {};

            this.summary = {
              ...emptySummary(),
              ...(stats.summary ?? {}),
            };

            this.byType =
              stats.by_type ?? [];

            this.bySource =
              stats.by_source ?? [];

            this.byCampaign =
              stats.by_campaign ?? [];

            this.byMalware =
              stats.by_malware ?? [];

            this.byMonth =
              stats.by_month ?? [];

            this.health =
              healthResult.status ===
              "fulfilled"
                ? healthResult.value
                : null;

            this.loaded = true;

          } catch (error) {
            console.error(
              "Dashboard load error:",
              error,
            );

            this.error = error;

            this.errorMessage =
              error.response?.data?.detail ??
              error.message ??
              "Error desconocido.";

          } finally {
            this.loading = false;
          }
        },

        resetDashboard() {
          this.$reset();
        },
      },
    },
  );
