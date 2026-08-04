import client from "./client";

const IOCApi = {
  async list(params = {}) {
    const normalizedParams = {
      page: 1,
      page_size: 25,
      ...params,
    };

    if (normalizedParams.page_size < 10) {
      normalizedParams.page_size = 10;
    }

    const response = await client.get(
      "/v2/iocs",
      {
        params: normalizedParams,
      },
    );

    return response.data;
  },

  async detail(id) {
    if (!id) {
      throw new Error(
        "Se requiere el identificador del IOC.",
      );
    }

    const response = await client.get(
      `/v2/iocs/${id}/details`,
    );

    return response.data;
  },

  async exportCsv(params = {}) {
    const response = await client.get(
      "/v2/iocs/export",
      {
        params,
        responseType: "blob",
      },
    );

    return response.data;
  },
};

export default IOCApi;
