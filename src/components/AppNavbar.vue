<script setup>
import { useRoute } from 'vue-router'
import { useTheme } from '@/composables/useTheme'
import { useSidebar } from '@/composables/useSidebar'

const route = useRoute()
const { isDark, toggleTheme } = useTheme()
const { isCollapsed, toggleSidebar } = useSidebar()
</script>

<template>
  <header class="app-navbar">
    <button
      v-if="route.path === '/mapa'"
      class="toggle-btn toggle-btn--collapse"
      :title="isCollapsed ? 'Expandir Sidebar' : 'Recolher Sidebar'"
      :aria-label="isCollapsed ? 'Expandir painel lateral' : 'Recolher painel lateral'"
      :aria-expanded="!isCollapsed"
      @click="toggleSidebar"
    >
      <i class="bi" :class="isCollapsed ? 'bi-chevron-right' : 'bi-chevron-left'" />
    </button>

    <RouterLink to="/" class="navbar-brand">
      <span class="brand-logo" aria-hidden="true"><i class="bi bi-geo-alt-fill" /></span>
      <span class="brand-name">INSA <span class="brand-accent">WebGIS</span></span>
    </RouterLink>

    <nav class="navbar-links" aria-label="Navegação principal">
      <RouterLink to="/" class="nav-link" exact-active-class="is-active">
        <i class="bi bi-house" aria-hidden="true" /> Início
      </RouterLink>
      <RouterLink to="/mapa" class="nav-link" active-class="is-active">
        <i class="bi bi-map" aria-hidden="true" /> Mapa
      </RouterLink>
      <RouterLink to="/dashboard" class="nav-link" active-class="is-active">
        <i class="bi bi-bar-chart-line" aria-hidden="true" /> Dashboard
      </RouterLink>
    </nav>

    <button
      class="toggle-btn"
      :title="isDark ? 'Mudar para tema claro' : 'Mudar para tema escuro'"
      :aria-label="isDark ? 'Ativar tema claro' : 'Ativar tema escuro'"
      @click="toggleTheme"
    >
      <i class="bi" :class="isDark ? 'bi-sun' : 'bi-moon-stars'" />
    </button>
  </header>
</template>

<style scoped>
.app-navbar {
  height: 52px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 0 16px;
  background: var(--bg-sidebar);
  border-bottom: 1px solid var(--border-color);
  z-index: 1200;
  position: relative;
}

.navbar-brand {
  display: flex;
  align-items: center;
  gap: 10px;
  text-decoration: none;
  flex-shrink: 0;
}

.brand-logo {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: var(--accent);
  color: #ffffff;
  font-size: 13px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.brand-name {
  font-size: 15px;
  font-weight: 600;
  letter-spacing: -0.3px;
  color: var(--text-main);
  white-space: nowrap;
}

.brand-accent {
  color: var(--accent);
}

.navbar-links {
  display: flex;
  align-items: center;
  gap: 4px;
  flex: 1;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border-radius: 8px;
  color: var(--text-muted);
  text-decoration: none;
  font-size: 13px;
  font-weight: 500;
  transition:
    background 0.15s,
    color 0.15s;
}

.nav-link:hover {
  background: var(--btn-bg-hover);
  color: var(--text-main);
}

.nav-link.is-active {
  background: var(--bg-accent-dim);
  color: var(--accent);
}

.toggle-btn {
  width: 30px;
  height: 30px;
  border-radius: 8px;
  border: none;
  background: var(--btn-bg);
  color: var(--text-muted);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  flex-shrink: 0;
  transition:
    background 0.15s,
    color 0.15s;
}

.toggle-btn:hover {
  background: var(--btn-bg-hover);
  color: var(--text-main);
}

.toggle-btn:active {
  transform: scale(0.95);
}
</style>
