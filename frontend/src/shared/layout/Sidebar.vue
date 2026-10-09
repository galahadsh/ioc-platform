<template>
  <aside class="enterprise-sidebar">

    <div class="enterprise-brand">
      <div class="enterprise-brand-mark">IP</div>
      <div>
        <strong>IOC Platform</strong>
        <span>Threat Intelligence</span>
      </div>
    </div>

    <nav class="enterprise-nav" aria-label="Navegación principal">

      <RouterLink class="enterprise-nav-link" to="/" exact-active-class="is-active">
        <span>⌂</span> Dashboard
      </RouterLink>

      <div class="enterprise-nav-section">
        Threat Intelligence
      </div>

      <RouterLink class="enterprise-nav-link" to="/explorer" active-class="is-active">
        <span>⌕</span> IOC Explorer
      </RouterLink>

      <RouterLink class="enterprise-nav-link" to="/campaigns" active-class="is-active">
        <span>◎</span> Campaigns
      </RouterLink>

      <RouterLink class="enterprise-nav-link" to="/malware" active-class="is-active">
        <span>◆</span> Malware
      </RouterLink>

      <RouterLink class="enterprise-nav-link" to="/actors" active-class="is-active">
        <span>◉</span> Threat Actors
      </RouterLink>

      <div class="enterprise-nav-section">
        Operations
      </div>

      <RouterLink class="enterprise-nav-link" to="/documents" active-class="is-active">
        <span>▧</span> Document Center
      </RouterLink>

      <RouterLink class="enterprise-nav-link" to="/cases" active-class="is-active">
        <span>▣</span> Cases
      </RouterLink>

      <RouterLink class="enterprise-nav-link" to="/reports" active-class="is-active">
        <span>▤</span> Reports
      </RouterLink>

    </nav>

    <div class="enterprise-sidebar-footer">
      <span>IOC Platform Enterprise</span>
      <small>v1.0 Preview</small>
    </div>

  </aside>
</template>

<style scoped>
.enterprise-sidebar {
  position: sticky;
  top: 0;
  display: flex;
  flex-direction: column;
  height: 100vh;
  overflow-y: auto;
  padding: 20px 15px;
  border-right: 1px solid #1d3a50;
  background: linear-gradient(180deg, #0b1d2c, #05111b);
  color: #eef5fa;
}

.enterprise-brand {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 10px 22px;
}

.enterprise-brand-mark {
  display: grid;
  place-items: center;
  width: 40px;
  height: 40px;
  flex-shrink: 0;
  border-radius: 11px;
  background: linear-gradient(145deg, #1683ff, #075eb7);
  box-shadow: 0 10px 25px rgba(22,131,255,.23);
  font-size: 13px;
  font-weight: 900;
}

.enterprise-brand strong,
.enterprise-brand span {
  display: block;
}

.enterprise-brand strong {
  font-size: 14px;
}

.enterprise-brand span {
  margin-top: 3px;
  color: #8198aa;
  font-size: 10px;
}

.enterprise-nav {
  display: grid;
  align-content: start;
  gap: 4px;
}

.enterprise-nav-section {
  margin: 19px 10px 7px;
  color: #4f6b7e;
  font-size: 10px;
  font-weight: 800;
  letter-spacing: .08em;
  text-transform: uppercase;
}

.enterprise-nav-link {
  display: flex;
  align-items: center;
  gap: 11px;
  min-height: 40px;
  padding: 0 12px;
  border: 1px solid transparent;
  border-radius: 8px;
  color: #93a8b7;
  font-size: 12px;
  font-weight: 600;
  text-decoration: none;
  transition: background .16s, color .16s, border-color .16s;
}

.enterprise-nav-link span {
  width: 18px;
  color: #5c92b7;
  text-align: center;
}

.enterprise-nav-link:hover {
  border-color: rgba(74,133,173,.24);
  background: rgba(21,64,91,.28);
  color: #e9f2f8;
}

.enterprise-nav-link.is-active {
  border-color: rgba(22,131,255,.36);
  background: linear-gradient(
    90deg,
    rgba(22,131,255,.18),
    rgba(22,131,255,.05)
  );
  color: #fff;
  box-shadow: inset 3px 0 0 #1683ff;
}

.enterprise-sidebar-footer {
  display: grid;
  gap: 4px;
  margin-top: auto;
  padding: 17px 11px 3px;
  border-top: 1px solid rgba(85,130,160,.22);
  color: #8198aa;
  font-size: 10px;
}

.enterprise-sidebar-footer small {
  color: #49677a;
}
</style>
