import client from "@/api/client";

const MINIMUM_PAGE_SIZE = 10;

const ExplorerApi = {
  async list(params = {}) {
    const requestedPageSize = Number(
      params.page_size ?? 25,
    );

    const pageSize = Math.max(
      requestedPageSize,
      MINIMUM_PAGE_SIZE,
    );

    const normalizedParams = {
      page: 1,
      ...params,
      page_size: pageSize,
    };

    const response = await client.get(
      "/v2/iocs",
      {
        params: normalizedParams,
      },
    );

    return response.data;
  },

  async detail(id) {
    const numericId = Number(id);

    if (
      !Number.isInteger(numericId) ||
      numericId <= 0
    ) {
      throw new Error(
        "El identificador del IOC no es válido.",
      );
    }

    const response = await client.get(
      `/v2/iocs/${numericId}/details`,
    );

    return response.data;
  },
};

export default ExplorerApi;
