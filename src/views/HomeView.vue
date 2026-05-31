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
    background: rgba(0, 0, 0, 0.4);
    opacity: 0;
    pointer-events: none;
    transition: opacity 0.25s ease;
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
    top: 12px;
    right: 12px;
    z-index: 1000;
    width: 44px;
    height: 44px;
    border-radius: 50%;
    border: none;
    background: rgba(255, 255, 255, 0.82);
    backdrop-filter: saturate(180%) blur(20px);
    -webkit-backdrop-filter: saturate(180%) blur(20px);
    color: #1d1d1f;
    font-size: 18px;
    cursor: pointer;
    box-shadow: rgba(0, 0, 0, 0.22) 3px 5px 30px 0;
    transition: opacity 0.2s ease, transform 0.2s ease, background 0.15s;
  }

  [data-theme="dark"] .sidebar-fab {
    background: rgba(28, 28, 30, 0.85);
    color: #f5f5f7;
  }

  .sidebar-fab:hover {
    background: #0066cc;
    color: #ffffff;
  }

  .sidebar-fab:active {
    transform: scale(0.95);
  }

  .sidebar-fab.is-hidden {
    opacity: 0;
    pointer-events: none;
    transform: scale(0.8);
  }
}
</style>
