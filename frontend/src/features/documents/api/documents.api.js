import client from "@/api/client";

const DocumentsApi = {
  async list(params = {}) {
    const response = await client.get(
      "/v3/documents",
      {
        params: {
          page: 1,
          page_size: 25,
          ...params,
        },
      },
    );

    return response.data;
  },

  async upload({
    file,
    source,
    tlp,
    classification,
    uploadedBy,
  }) {
    const formData = new FormData();

    formData.append(
      "file",
      file,
    );

    if (source) {
      formData.append(
        "source",
        source,
      );
    }

    if (tlp) {
      formData.append(
        "tlp",
        tlp,
      );
    }

    if (classification) {
      formData.append(
        "classification",
        classification,
      );
    }

    if (uploadedBy) {
      formData.append(
        "uploaded_by",
        uploadedBy,
      );
    }

    const response = await client.post(
      "/v3/documents",
      formData,
    );

    return response.data;
  },

  async detail(id) {
    const response = await client.get(
      `/v3/documents/${id}`,
    );

    return response.data;
  },

  async download(id) {
    const response = await client.get(
      `/v3/documents/${id}/download`,
      {
        responseType: "blob",
      },
    );

    return response;
  },
};

export default DocumentsApi;
