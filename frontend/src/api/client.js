import axios from "axios";

const client = axios.create({
  baseURL: "/api",
  timeout: 30000,
  headers: {
    Accept: "application/json",
    "Content-Type": "application/json",
  },
});

client.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error.response?.status;
    const detail =
      error.response?.data?.detail ||
      error.message ||
      "Error de comunicación con la API";

    console.error("API Error:", {
      status,
      detail,
      url: error.config?.url,
    });

    return Promise.reject(error);
  },
);

export default client;
