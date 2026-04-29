<script setup>
import { ref } from 'vue'
import { useMapStore } from '@/stores/mapStore'
import LayerCard from './LayerCard.vue'

const store = useMapStore()
const isCollapsed = ref(false)

function toggle() {
  isCollapsed.value = !isCollapsed.value
}
</script>

<template>
  <aside id="sidebar" :class="{ collapsed: isCollapsed }">

    <!-- Cabeçalho -->
    <div class="sidebar-header">
      <div class="brand-wrapper">
        <div class="brand-logo">
          <i class="bi bi-geo-alt-fill" />
        </div>
        <div class="brand-name">
          INSA <span class="brand-accent">WebGIS</span>
        </div>
      </div>
      <button class="toggle-btn" title="Alternar sidebar" @click="toggle">
        <i class="bi" :class="isCollapsed ? 'bi-chevron-right' : 'bi-chevron-left'" />
      </button>
    </div>

    <!-- Conteúdo -->
    <div class="sidebar-content">

      <!-- Seção: Camadas Base -->
      <div class="section-title">
        <span>Camadas Base</span>
        <span class="count-badge">{{ store.availableBaseLayers.length }}</span>
      </div>

      <LayerCard
        v-for="layer in store.availableBaseLayers"
        :key="layer.key"
        type="base"
        :layer-key="layer.key"
        :label="layer.label"
        :meta="layer.meta"
        :collapsed="isCollapsed"
      />

      <!-- Seção: Sobreposição -->
      <div class="section-title section-title--gap">
        <span>Sobreposição</span>
        <span class="count-badge">{{ store.availableOverlays.length }}</span>
      </div>

      <LayerCard
        v-for="layer in store.availableOverlays"
        :key="layer.key"
        type="overlay"
        :layer-key="layer.key"
        :label="layer.label"
        :meta="layer.meta"
        :legend="layer.legend"
        :search-fields="layer.searchFields"
        :collapsed="isCollapsed"
      />

    </div>

    <!-- Rodapé -->
    <div class="sidebar-footer">
      <i class="bi bi-hdd-network-fill footer-icon" />
      <span>EPSG:4326 | Online</span>
    </div>

  </aside>
</template>

<style scoped>
#sidebar {
  width: var(--sidebar-w);
  background: var(--bg-sidebar);
  border-right: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  transition: width var(--transition-speed) var(--transition-curve);
  position: relative;
  z-index: 1000;
  box-shadow: var(--shadow-lg);
  overflow: hidden;
}

#sidebar.collapsed {
  width: var(--sidebar-collapsed-w);
}

/* ── Cabeçalho ── */
.sidebar-header {
  height: 70px;
  padding: 0 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid var(--border-color);
  flex-shrink: 0;
}

.brand-wrapper {
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 200px;
  transition: opacity 0.2s;
}

#sidebar.collapsed .brand-wrapper {
  opacity: 0;
  pointer-events: none;
}

.brand-logo {
  width: 32px;
  height: 32px;
  background: linear-gradient(135deg, var(--accent), var(--accent-secondary));
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #000;
  font-size: 1.1rem;
  box-shadow: 0 0 15px rgba(0, 212, 170, 0.3);
  flex-shrink: 0;
}

.brand-name {
  font-weight: 700;
  font-size: 1.1rem;
  letter-spacing: -0.02em;
  color: var(--text-main);
  white-space: nowrap;
}

.brand-accent {
  color: var(--accent);
}

.toggle-btn {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  color: var(--text-muted);
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
  flex-shrink: 0;
}

.toggle-btn:hover {
  background: var(--accent);
  color: #000;
  border-color: var(--accent);
}

#sidebar.collapsed .toggle-btn {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
}

/* ── Conteúdo ── */
.sidebar-content {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 16px 0;
}

.sidebar-content::-webkit-scrollbar {
  width: 5px;
}

.sidebar-content::-webkit-scrollbar-thumb {
  background: var(--border-color);
  border-radius: 10px;
}

.section-title {
  padding: 0 20px 8px;
  font-size: 0.7rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--text-dim);
  display: flex;
  align-items: center;
  justify-content: space-between;
  white-space: nowrap;
  overflow: hidden;
}

.section-title--gap {
  margin-top: 1.5rem;
}

#sidebar.collapsed .section-title span,
#sidebar.collapsed .count-badge {
  display: none;
}

.count-badge {
  background: transparent;
  border: 1px solid var(--border-color);
  color: var(--text-dim);
  font-size: 0.65rem;
  border-radius: 20px;
  padding: 1px 7px;
}

/* Oculta info textual dos cards quando colapsado */
#sidebar.collapsed :deep(.layer-info),
#sidebar.collapsed :deep(.layer-actions-top) {
  display: none;
}

/* ── Rodapé ── */
.sidebar-footer {
  padding: 15px 20px;
  border-top: 1px solid var(--border-color);
  font-size: 0.7rem;
  color: var(--text-dim);
  display: flex;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
  white-space: nowrap;
  overflow: hidden;
}

.footer-icon {
  color: var(--accent);
  flex-shrink: 0;
}

#sidebar.collapsed .sidebar-footer span {
  display: none;
}
</style>
