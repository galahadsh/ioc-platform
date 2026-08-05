<template>
  <div class="layout">
    <Sidebar />

    <div class="main">
      <Header />

      <main class="content">
        <RouterView />
      </main>
    </div>
  </div>
</template>

<script setup>
import Sidebar from
  "@/shared/layout/Sidebar.vue";

import Header from
  "@/shared/layout/Header.vue";
</script>

<style scoped>
.layout {
  display: grid;
  grid-template-columns:
    250px
    minmax(0, 1fr);
  min-height: 100vh;
  background:
    var(--background);
}

.main {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.content {
  flex: 1;
  min-width: 0;
  overflow: auto;
}

@media (max-width: 760px) {
  .layout {
    grid-template-columns: 1fr;
  }
}
</style>
