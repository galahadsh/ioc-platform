<template>
  <header class="header">
    <div class="header-left">
      <div class="page-title">
        IOC Platform Enterprise
      </div>
      <div class="breadcrumb">
        Cyber Threat Intelligence
      </div>
    </div>

    <div class="header-center">
      <input
        class="search"
        type="text"
        placeholder="Buscar IOC, Campaign, Malware..."
      />
    </div>

    <div class="header-right">
      <button class="icon-button" title="Actualizar" @click="reload">
        🔄
      </button>

      <button class="icon-button" title="Notificaciones" disabled>
        🔔
      </button>

      <div class="user">
        <div class="avatar">{{ initials }}</div>

        <div>
          <div class="user-name">{{ displayName }}</div>
          <div class="user-role">{{ displayRole }}</div>
        </div>
      </div>

      <button
        class="logout-button"
        type="button"
        @click="logout"
      >
        Cerrar sesión
      </button>
    </div>
  </header>
</template>

<script setup>
import { computed } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "@/stores/auth.store";

const router = useRouter();
const auth = useAuthStore();

const displayName = computed(
  () => auth.user?.full_name || auth.user?.username || "Usuario"
);

const displayRole = computed(
  () => auth.user?.roles?.join(", ") || "Sin rol"
);

const initials = computed(() => {
  const name = displayName.value.trim();
  return name
    .split(/\\s+/)
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase() || "")
    .join("");
});

function logout() {
  auth.clearSession();
  router.replace("/login");
}

function reload() {
  window.location.reload();
}
</script>

<style scoped>

.header{

    display:flex;

    justify-content:space-between;

    align-items:center;

    height:72px;

    padding:0 28px;

    background:#162131;

    border-bottom:1px solid #223449;

}

.header-left{

    display:flex;

    flex-direction:column;

}

.page-title{

    color:white;

    font-size:22px;

    font-weight:700;

}

.breadcrumb{

    color:#8CA0B3;

    font-size:12px;

}

.header-center{

    flex:1;

    display:flex;

    justify-content:center;

}

.search{

    width:420px;

    padding:10px 15px;

    border:none;

    border-radius:8px;

    background:#0D1725;

    color:white;

    outline:none;

}

.search::placeholder{

    color:#607386;

}

.header-right{

    display:flex;

    align-items:center;

    gap:18px;

}

.icon-button{

    width:40px;

    height:40px;

    border:none;

    border-radius:8px;

    background:#0D1725;

    color:white;

    cursor:pointer;

    transition:.2s;

}

.icon-button:hover{

    background:#1D2E45;

}

.user{

    display:flex;

    align-items:center;

    gap:10px;

}

.avatar{

    width:42px;

    height:42px;

    border-radius:50%;

    display:flex;

    justify-content:center;

    align-items:center;

    background:#3B82F6;

    color:white;

    font-weight:bold;

}

.user-name{

    color:white;

    font-size:14px;

    font-weight:600;

}

.user-role{

    color:#8CA0B3;

    font-size:12px;

}


.logout-button {
  padding: 10px 14px;
  border: 1px solid #334155;
  border-radius: 8px;
  background: #0d1725;
  color: #f1f5f9;
  cursor: pointer;
}

.logout-button:hover {
  background: #1d2e45;
}

.logout-button:focus-visible {
  outline: 2px solid #38bdf8;
}
</style>