import axios from "axios";
import { useAuthStore } from "@/stores/auth.store";

const client = axios.create({
  baseURL: "/api",
  timeout: 30000,
  headers: {
    Accept: "application/json",
  },
});

client.interceptors.request.use((config) => {
  const auth = useAuthStore();

  if (auth.accessToken) {
    config.headers.Authorization =
      `Bearer ${auth.accessToken}`;
  }

  return config;
});

client.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error.response?.status;

    if (status === 401) {
      const auth = useAuthStore();
      auth.clearSession();
    }

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
  }
);

export default client;
