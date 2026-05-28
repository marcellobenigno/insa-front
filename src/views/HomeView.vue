<script setup>
import AppSidebar from '@/components/AppSidebar.vue'
import MapContainer from '@/components/MapContainer.vue'
import CoordDisplay from '@/components/CoordDisplay.vue'
import { useSidebar } from '@/composables/useSidebar'

const { isCollapsed, toggleSidebar } = useSidebar()
</script>

<template>
  <div class="home-view">
    <div
      class="sidebar-backdrop"
      :class="{ 'is-visible': !isCollapsed }"
      aria-hidden="true"
      @click="toggleSidebar"
    />
    <AppSidebar />
    <main class="map-area">
      <MapContainer />
      <CoordDisplay />
      <button
        class="sidebar-fab"
        :class="{ 'is-hidden': !isCollapsed }"
        aria-label="Abrir painel de camadas"
        @click="toggleSidebar"
      >
        <i class="bi bi-layers-fill" aria-hidden="true" />
      </button>
    </main>
  </div>
</template>

<style scoped>
.home-view {
  display: flex;
  width: 100%;
  height: 100%;
}

.map-area {
  flex: 1;
  position: relative;
  overflow: hidden;
  background: var(--bg-app);
}

/* ── Backdrop (mobile only) ──────────────────────────────────────────────────── */
.sidebar-backdrop {
  display: none;
}

/* ── FAB para reabrir a sidebar (mobile only) ────────────────────────────────── */
.sidebar-fab {
  display: none;
}

@media (max-width: 768px) {
  .sidebar-backdrop {
    display: block;
    position: fixed;
    inset: 0;
    z-index: 1090;
    background: rgba(0, 0, 0, 0.5);
    opacity: 0;
    pointer-events: none;
    transition: opacity 0.3s ease;
  }

  .sidebar-backdrop.is-visible {
    opacity: 1;
    pointer-events: auto;
  }

  .sidebar-fab {
    display: flex;
    align-items: center;
    justify-content: center;
    position: absolute;
    top: 14px;
    left: 14px;
    z-index: 1000;
    width: 44px;
    height: 44px;
    border-radius: 12px;
    border: 1px solid var(--border-color);
    background: var(--bg-sidebar);
    color: var(--text-muted);
    font-size: 1.2rem;
    cursor: pointer;
    box-shadow: var(--shadow-lg);
    transition: opacity 0.2s ease, transform 0.2s ease, background 0.2s, color 0.2s;
  }

  .sidebar-fab:hover {
    background: var(--accent);
    color: var(--text-on-accent);
    border-color: var(--accent);
  }

  .sidebar-fab.is-hidden {
    opacity: 0;
    pointer-events: none;
    transform: scale(0.8);
  }
}
</style>
