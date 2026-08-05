import {
  defineStore,
} from "pinia";

import IOCApi from
  "@/api/ioc.api";

const emptyPagination = () => ({
  page: 1,
  page_size: 25,
  total: 0,
  total_pages: 0,
  has_previous: false,
  has_next: false,
});

export const useExplorerStore =
  defineStore(
    "explorer",
    {
      state: () => ({
        items: [],
        pagination:
          emptyPagination(),

        loading: false,
        loaded: false,

        error: null,
        errorMessage: "",

        selectedIOC: null,

        filters: {
          search: "",
          tipo: "",
          estado: "",
          fuente: "",
          campaign: "",
          malware_family: "",
        },
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
      },

      actions: {
        async loadIOCs() {
          if (this.loading) {
            return;
          }

          this.loading = true;
          this.error = null;
          this.errorMessage = "";

          try {
            const response =
              await IOCApi.list({
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
              "Explorer load error:",
              error
            );

            this.items = [];
            this.error = error;

            this.errorMessage =
              error.response
                ?.data
                ?.detail ??
              error.message ??
              "No fue posible obtener los IOC.";

          } finally {
            this.loading = false;
          }
        },

        normalizedFilters() {
          return Object.fromEntries(
            Object.entries(
              this.filters
            ).filter(([, value]) => {
              return (
                value !== null &&
                value !== undefined &&
                String(value).trim() !== ""
              );
            })
          );
        },

        async goToPage(page) {
          const numericPage =
            Number(page);

          if (
            !Number.isInteger(
              numericPage
            ) ||
            numericPage < 1 ||
            (
              this.pagination.total_pages >
                0 &&
              numericPage >
                this.pagination.total_pages
            )
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
            this.pagination.page - 1
          );
        },

        async nextPage() {
          if (!this.hasNext) {
            return;
          }

          await this.goToPage(
            this.pagination.page + 1
          );
        },

        async setPageSize(pageSize) {
          const normalized =
            Math.max(
              Number(pageSize) || 25,
              10
            );

          this.pagination.page_size =
            normalized;

          this.pagination.page = 1;

          await this.loadIOCs();
        },

        selectIOC(ioc) {
          this.selectedIOC =
            ioc ?? null;
        },

        clearSelection() {
          this.selectedIOC = null;
        },

        async refresh() {
          await this.loadIOCs();
        },
      },
    }
  );
