<template>
  <div class="password-page">
    <form class="password-card" @submit.prevent="submit">
      <div class="shield">🛡</div>
      <h1>Actualizar contraseña</h1>
      <p>
        Por seguridad, debes establecer una nueva
        contraseña antes de utilizar la plataforma.
      </p>

      <label>Contraseña actual</label>
      <input
        v-model="currentPassword"
        type="password"
        autocomplete="current-password"
        required
      />

      <label>Nueva contraseña</label>
      <input
        v-model="newPassword"
        type="password"
        autocomplete="new-password"
        minlength="12"
        required
      />

      <label>Confirmar nueva contraseña</label>
      <input
        v-model="confirmation"
        type="password"
        autocomplete="new-password"
        minlength="12"
        required
      />

      <p v-if="error" class="error" role="alert">
        {{ error }}
      </p>

      <button :disabled="loading">
        {{ loading ? "Actualizando..." : "Cambiar contraseña" }}
      </button>
    </form>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "@/stores/auth.store";
import client from "@/api/client";

const router = useRouter();
const auth = useAuthStore();

const currentPassword = ref("");
const newPassword = ref("");
const confirmation = ref("");
const loading = ref(false);
const error = ref("");

async function submit() {
  error.value = "";

  if (newPassword.value !== confirmation.value) {
    error.value = "Las contraseñas no coinciden.";
    return;
  }

  if (newPassword.value.length < 12) {
    error.value = "La contraseña debe tener al menos 12 caracteres.";
    return;
  }

  loading.value = true;

  try {
    await client.post("/v1/auth/change-password", {
      current_password: currentPassword.value,
      new_password: newPassword.value,
    });

    // No reutilizar credenciales o tokens previos.
    auth.clearSession();

    await router.replace({
      name: "login",
      query: { passwordChanged: "1" },
    });
  } catch (err) {
    const detail = err.response?.data?.detail;
    error.value =
      typeof detail === "string"
        ? detail
        : "No fue posible actualizar la contraseña.";
  } finally {
    currentPassword.value = "";
    newPassword.value = "";
    confirmation.value = "";
    loading.value = false;
  }
}
</script>

<style scoped>
.password-page {
  min-height: 100vh;
  display: grid;
  place-items: center;
  padding: 24px;
  background: #0b1120;
}

.password-card {
  width: min(100%, 440px);
  display: flex;
  flex-direction: column;
  gap: 14px;
  padding: 36px;
  background: #151f30;
  border: 1px solid #26354b;
  border-radius: 16px;
  color: #f1f5f9;
}

.shield {
  text-align: center;
  font-size: 36px;
}

h1 {
  margin: 0;
  text-align: center;
}

p {
  color: #94a3b8;
  font-size: 13px;
  line-height: 1.6;
}

label {
  font-size: 13px;
  font-weight: 600;
}

input {
  padding: 13px;
  border: 1px solid #334155;
  border-radius: 8px;
  background: #0f172a;
  color: white;
}

button {
  padding: 14px;
  border: 0;
  border-radius: 8px;
  background: #2563eb;
  color: white;
  font-weight: 700;
  cursor: pointer;
}

button:disabled {
  opacity: 0.6;
}

.error {
  color: #fca5a5;
}
</style>
