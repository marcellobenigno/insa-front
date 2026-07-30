<script setup>
import { useTheme } from '@/composables/useTheme'
import logoMark from '@/assets/logo-mark-coarse.svg'

const { isDark, toggleTheme } = useTheme()
</script>

<template>
  <header class="app-navbar">
    <RouterLink to="/" class="navbar-brand" aria-label="DesertPB — Início">
      <img :src="logoMark" class="brand-logo" alt="" aria-hidden="true" />
    </RouterLink>

    <nav class="navbar-links" aria-label="Navegação principal">
      <RouterLink to="/" class="nav-link" title="Início" exact-active-class="is-active">
        <i class="bi bi-house" aria-hidden="true" /> <span class="nav-link-label">Início</span>
      </RouterLink>
      <RouterLink to="/mapa" class="nav-link" title="Mapa" active-class="is-active">
        <i class="bi bi-map" aria-hidden="true" /> <span class="nav-link-label">Mapa</span>
      </RouterLink>
      <RouterLink
        to="/dashboard"
        class="nav-link"
        title="Painel Interativo"
        active-class="is-active"
      >
        <i class="bi bi-bar-chart-line" aria-hidden="true" />
        <span class="nav-link-label">Painel Interativo</span>
      </RouterLink>
      <RouterLink to="/sobre" class="nav-link" title="Sobre" active-class="is-active">
        <i class="bi bi-info-circle" aria-hidden="true" /> <span class="nav-link-label">Sobre</span>
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
  height: 26px;
  width: auto;
  flex-shrink: 0;
  display: block;
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

@media (max-width: 480px) {
  .app-navbar {
    gap: 8px;
    padding: 0 10px;
  }

  .navbar-links {
    gap: 0;
    justify-content: space-between;
  }

  .nav-link {
    padding: 6px 8px;
  }

  .nav-link-label {
    display: none;
  }
}
</style>
