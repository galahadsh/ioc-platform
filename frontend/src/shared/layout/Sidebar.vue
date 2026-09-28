<template>
  <aside class="sidebar">
    <div class="logo">
      <div class="logo-icon">
        🛡
      </div>

      <div>
        <div class="logo-title">
          Cyber Intelligence
        </div>

        <div class="logo-subtitle">
          Platform
        </div>
      </div>
    </div>

    <div class="section">
      GENERAL
    </div>

    <RouterLink to="/">
      📊 Dashboard
    </RouterLink>

    <div class="section">
      INGESTA
    </div>

    <RouterLink to="/documents">
      📄 Document Center
    </RouterLink>

    <div class="section">
      THREAT INTELLIGENCE
    </div>

    <RouterLink to="/explorer">
      🔎 IOC Explorer
    </RouterLink>

    <RouterLink to="/campaigns">
      🎯 Campaigns
    </RouterLink>

    <RouterLink to="/malware">
      🦠 Malware
    </RouterLink>

    <RouterLink to="/actors">
      👤 Threat Actors
    </RouterLink>

    <div class="section">
      OPERATIONS
    </div>

    <RouterLink to="/cases">
      📁 Cases
    </RouterLink>

    <RouterLink to="/reports">
      📑 Reports
    </RouterLink>

    <div class="footer">
      Version 1.0 Alpha
    </div>
  </aside>
</template>

<script setup>
</script>

<style scoped>
.sidebar {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  padding: 25px;
  gap: 8px;
  background: var(--surface);
  border-right: 1px solid var(--border);
}

.logo {
  display: flex;
  gap: 12px;
  align-items: center;
  margin-bottom: 30px;
}

.logo-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  border-radius: var(--radius-md);
  background: var(--primary);
  font-size: 22px;
}

.logo-title {
  color: var(--text);
  font-size: 16px;
  font-weight: 800;
}

.logo-subtitle {
  color: var(--text-muted);
  font-size: 12px;
}

.section {
  margin-top: 20px;
  margin-bottom: 8px;
  color: var(--text-muted);
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 1px;
}

a {
  padding: 12px;
  border-radius: var(--radius-sm);
  color: var(--text-muted);
  text-decoration: none;
  font-size: 14px;
  transition: var(--transition);
}

a:hover {
  background: var(--surface-hover);
  color: var(--text);
}

.router-link-active {
  background: var(--primary);
  color: white;
}

.footer {
  margin-top: auto;
  color: var(--text-muted);
  font-size: 12px;
}
</style>
