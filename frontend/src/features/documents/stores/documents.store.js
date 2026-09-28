import {
  defineStore,
} from "pinia";

import DocumentsApi from
  "@/features/documents/api/documents.api";

export const useDocumentsStore =
  defineStore(
    "documents",
    {
      state: () => ({
        items: [],

        pagination: {
          page: 1,
          page_size: 25,
          total: 0,
          pages: 0,
        },

        loading: false,
        uploading: false,

        errorMessage: "",
        uploadMessage: "",
      }),

      getters: {
        totalDocuments: (state) =>
          state.pagination.total,

        hasPrevious: (state) =>
          state.pagination.page > 1,

        hasNext: (state) =>
          state.pagination.page <
          state.pagination.pages,
      },

      actions: {
        async loadDocuments() {
          this.loading = true;
          this.errorMessage = "";

          try {
            const data =
              await DocumentsApi.list({
                page:
                  this.pagination.page,

                page_size:
                  this.pagination.page_size,
              });

            this.items =
              data.items ?? [];

            this.pagination = {
              page:
                data.page ?? 1,

              page_size:
                data.page_size ?? 25,

              total:
                data.total ?? 0,

              pages:
                data.pages ?? 0,
            };
          } catch (error) {
            console.error(
              "Documents load error:",
              error,
            );

            this.errorMessage =
              error.response
                ?.data
                ?.detail ??
              error.message ??
              "No fue posible cargar los documentos.";
          } finally {
            this.loading = false;
          }
        },

        async uploadDocument(payload) {
          this.uploading = true;
          this.errorMessage = "";
          this.uploadMessage = "";

          try {
            const response =
              await DocumentsApi.upload(
                payload,
              );

            this.uploadMessage =
              response.message ??
              "Documento cargado.";

            this.pagination.page = 1;

            await this.loadDocuments();

            return response;
          } catch (error) {
            console.error(
              "Document upload error:",
              error,
            );

            this.errorMessage =
              error.response
                ?.data
                ?.detail ??
              error.message ??
              "No fue posible subir el documento.";

            throw error;
          } finally {
            this.uploading = false;
          }
        },

        async downloadDocument(document) {
          try {
            const response =
              await DocumentsApi.download(
                document.id,
              );

            const url =
              window.URL.createObjectURL(
                response.data,
              );

            const link =
              window.document.createElement(
                "a",
              );

            link.href = url;

            link.download =
              document.original_name;

            window.document.body.appendChild(
              link,
            );

            link.click();

            link.remove();

            window.URL.revokeObjectURL(
              url,
            );
          } catch (error) {
            console.error(
              "Document download error:",
              error,
            );

            this.errorMessage =
              "No fue posible descargar el documento.";
          }
        },

        async nextPage() {
          if (!this.hasNext) {
            return;
          }

          this.pagination.page += 1;

          await this.loadDocuments();
        },

        async previousPage() {
          if (!this.hasPrevious) {
            return;
          }

          this.pagination.page -= 1;

          await this.loadDocuments();
        },
      },
    },
  );
