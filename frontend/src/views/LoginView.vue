<template>
  <div class="login-page">
    <form class="login-card" @submit.prevent="submit">
      <div class="brand-icon">🛡</div>

      <h1>Cyber Intelligence</h1>
      <p class="subtitle">Enterprise Threat Intelligence Platform</p>

      <label for="username">Usuario</label>
      <input
        id="username"
        v-model.trim="username"
        autocomplete="username"
        required
        placeholder="Usuario"
      />

      <label for="password">Contraseña</label>
      <input
        id="password"
        v-model="password"
        type="password"
        autocomplete="current-password"
        required
        placeholder="Contraseña"
      />

      <p v-if="auth.error" class="error" role="alert">
        {{ auth.error }}
      </p>

      <button type="submit" :disabled="auth.loading">
        {{ auth.loading ? "Autenticando..." : "Iniciar sesión" }}
      </button>

      <p class="footer">IOC Platform Enterprise</p>
    </form>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "@/stores/auth.store";

const router = useRouter();
const auth = useAuthStore();

const username = ref("");
const password = ref("");

async function submit() {
  try {
    await auth.login(username.value, password.value);
    password.value = "";

    if (auth.mustChangePassword) {
      await router.replace("/change-password");
    } else {
      await router.replace("/");
    }
  } catch {
    password.value = "";
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: grid;
  place-items: center;
  padding: 24px;
  background: #0b1120;
}

.login-card {
  width: min(100%, 420px);
  display: flex;
  flex-direction: column;
  gap: 14px;
  padding: 36px;
  border: 1px solid #26354b;
  border-radius: 16px;
  background: #151f30;
  color: #f1f5f9;
}

.brand-icon {
  font-size: 40px;
  text-align: center;
}

h1 {
  margin: 0;
  text-align: center;
  font-size: 26px;
}

.subtitle {
  margin: 0 0 20px;
  text-align: center;
  color: #94a3b8;
  font-size: 13px;
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
  font: inherit;
}

input:focus {
  outline: 2px solid #38bdf8;
}

button {
  margin-top: 12px;
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
  cursor: wait;
}

.error {
  color: #fca5a5;
  font-size: 13px;
}

.footer {
  margin-top: 20px;
  text-align: center;
  color: #64748b;
  font-size: 12px;
}
</style>
