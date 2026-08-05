import {
  defineStore,
} from "pinia";

import ExplorerApi from
  "@/features/explorer/api/explorer.api";

const emptyPagination = () => ({
  page: 1,
  page_size: 25,
  total: 0,
  total_pages: 0,
  has_previous: false,
  has_next: false,
});

const emptyFilters = () => ({
  search: "",
  tipo: "",
  estado: "",
  fuente: "",
  campaign: "",
  malware_family: "",
});

export const useExplorerStore =
  defineStore(
    "explorer",
    {
      state: () => ({
        items: [],

        pagination:
          emptyPagination(),

        filters:
          emptyFilters(),

        loading: false,
        loaded: false,

        error: null,
        errorMessage: "",

        selectedRow: null,
        selectedDetail: null,

        drawerOpen: false,
        detailLoading: false,
        detailError: null,
        detailErrorMessage: "",
      }),

      getters: {
        totalIOCs: (state) =>
          state.pagination.total,

        currentPage: (state) =>
          state.pagination.page,

        totalPages: (state) =>
          state.pagination.total_pages,

        hasPrevious: (state) =>
          state.pagination.has_previous,

        hasNext: (state) =>
          state.pagination.has_next,

        selectedIOC: (state) =>
          state.selectedDetail?.ioc ??
          null,

        selectedVirusTotal: (state) =>
          state.selectedDetail
            ?.virustotal ??
          null,

        selectedGeolocation: (state) =>
          state.selectedDetail
            ?.geolocation ??
          null,
      },

      actions: {
        normalizedFilters() {
          return Object.fromEntries(
            Object.entries(
              this.filters,
            ).filter(([, value]) => {
              return (
                value !== null &&
                value !== undefined &&
                String(value).trim() !== ""
              );
            }),
          );
        },

        async loadIOCs() {
          if (this.loading) {
            return;
          }

          this.loading = true;
          this.error = null;
          this.errorMessage = "";

          try {
            const response =
              await ExplorerApi.list({
                page:
                  this.pagination.page,

                page_size:
                  this.pagination.page_size,

                ...this.normalizedFilters(),
              });

            this.items =
              response.items ?? [];

            this.pagination = {
              ...emptyPagination(),
              ...response.pagination,
            };

            this.loaded = true;
          } catch (error) {
            console.error(
              "Error cargando IOC:",
              error,
            );

            this.items = [];
            this.error = error;

            this.errorMessage =
              error.response
                ?.data
                ?.detail ??
              error.message ??
              "No fue posible cargar los IOC.";
          } finally {
            this.loading = false;
          }
        },

        async loadIOCDetail(ioc) {
          const id =
            typeof ioc === "object"
              ? ioc?.id
              : ioc;

          const numericId = Number(id);

          if (
            !Number.isInteger(
              numericId,
            ) ||
            numericId <= 0
          ) {
            return;
          }

          this.selectedRow =
            typeof ioc === "object"
              ? ioc
              : null;

          this.selectedDetail = null;
          this.detailError = null;
          this.detailErrorMessage = "";
          this.detailLoading = true;
          this.drawerOpen = true;

          try {
            this.selectedDetail =
              await ExplorerApi.detail(
                numericId,
              );
          } catch (error) {
            console.error(
              "Error cargando detalle:",
              error,
            );

            this.detailError = error;

            this.detailErrorMessage =
              error.response
                ?.data
                ?.detail ??
              error.message ??
              "No fue posible cargar el detalle del IOC.";
          } finally {
            this.detailLoading = false;
          }
        },

        closeDrawer() {
          this.drawerOpen = false;
          this.selectedRow = null;
          this.selectedDetail = null;
          this.detailError = null;
          this.detailErrorMessage = "";
          this.detailLoading = false;
        },

        async goToPage(page) {
          const numericPage =
            Number(page);

          if (
            !Number.isInteger(
              numericPage,
            ) ||
            numericPage < 1
          ) {
            return;
          }

          if (
            this.totalPages > 0 &&
            numericPage >
              this.totalPages
          ) {
            return;
          }

          this.pagination.page =
            numericPage;

          await this.loadIOCs();
        },

        async previousPage() {
          if (!this.hasPrevious) {
            return;
          }

          await this.goToPage(
            this.currentPage - 1,
          );
        },

        async nextPage() {
          if (!this.hasNext) {
            return;
          }

          await this.goToPage(
            this.currentPage + 1,
          );
        },

        async setPageSize(pageSize) {
          const normalizedPageSize =
            Math.max(
              Number(pageSize) || 25,
              10,
            );

          this.pagination.page_size =
            normalizedPageSize;

          this.pagination.page = 1;

          await this.loadIOCs();
        },

        async refresh() {
          await this.loadIOCs();
        },
      },
    },
  );
