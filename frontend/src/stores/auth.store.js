import { defineStore } from "pinia";
import { ref, computed } from "vue";
import axios from "axios";

export const useAuthStore = defineStore("auth", () => {
  const accessToken = ref(null);
  const user = ref(null);
  const loading = ref(false);
  const error = ref(null);

  const isAuthenticated = computed(
    () => Boolean(accessToken.value && user.value)
  );

  const mustChangePassword = computed(
    () => user.value?.must_change_password === true
  );

  const isAdmin = computed(
    () => user.value?.roles?.includes("ADMIN") ?? false
  );

  async function login(username, password) {
    loading.value = true;
    error.value = null;

    try {
      const response = await axios.post(
        "/api/v1/auth/login",
        {
          login: username,
          password,
        }
      );

      accessToken.value = response.data.access_token;
      user.value = response.data.user;

      return response.data;
    } catch (err) {
      error.value =
        err.response?.data?.detail ||
        "No fue posible iniciar sesión.";

      throw err;
    } finally {
      loading.value = false;
    }
  }

  function clearSession() {
    accessToken.value = null;
    user.value = null;
    error.value = null;
  }

  return {
    accessToken,
    user,
    loading,
    error,
    isAuthenticated,
    mustChangePassword,
    isAdmin,
    login,
    clearSession,
  };
});
