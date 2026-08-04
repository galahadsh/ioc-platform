import axios from "axios";
import client from "./client";

const DashboardApi = {
  async getStats() {
    const response = await client.get(
      "/stats/overview",
    );

    return response.data;
  },

  async getHealth() {
    const response = await axios.get(
      "/health",
      {
        timeout: 30000,
        headers: {
          Accept: "application/json",
        },
      },
    );

    return response.data;
  },
};

export default DashboardApi;
