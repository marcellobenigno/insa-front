<script setup>
import { computed, onMounted } from 'vue'
import { useMapStore } from '@/stores/mapStore'
import { OVERLAY_CATEGORIES } from '@/config/layers'
import { useSidebar } from '@/composables/useSidebar'
import LayerCard from './LayerCard.vue'

const store = useMapStore()
const { 
  isCollapsed, 
  openBase, 
  openCategories, 
  toggleSidebar, 
  toggleBase, 
  toggleCategory,
  initCategories 
} = useSidebar()

// Inicializa o estado das categorias baseado no config
onMounted(() => {
  initCategories(Object.keys(OVERLAY_CATEGORIES))
})

// Conta camadas visíveis por categoria para feedback visual no badge
function visibleCount(categoryKey) {
  const layers = OVERLAY_CATEGORIES[categoryKey].layers
  return Object.keys(layers).filter(k => store.visibleOverlays[k]).length
}

// Lista de categorias formatada para o v-for
const categoriesList = computed(() =>
  Object.entries(OVERLAY_CATEGORIES).map(([key, cat]) => ({
    key,
    ...cat,
    layerList: Object.entries(cat.layers).map(([lKey, l]) => ({ key: lKey, ...l })),
  }))
)
</script>

<template>
  <aside 
    id="sidebar" 
    :class="{ 'is-collapsed': isCollapsed }"
    role="complementary"
    aria-label="Painel de Controle do Mapa"
  >
    <!-- Cabeçalho -->
    <header class="sidebar-header">
      <div class="brand-wrapper" v-show="!isCollapsed">
        <div class="brand-logo" aria-hidden="true">
          <i class="bi bi-geo-alt-fill" />
        </div>
        <div class="brand-name">
          INSA <span class="brand-accent">WebGIS</span>
        </div>
      </div>
      <button 
        class="toggle-btn" 
        :title="isCollapsed ? 'Expandir Sidebar' : 'Recolher Sidebar'"
        :aria-label="isCollapsed ? 'Expandir painel lateral' : 'Recolher painel lateral'"
        :aria-expanded="!isCollapsed"
        @click="toggleSidebar"
      >
        <i class="bi" :class="isCollapsed ? 'bi-chevron-right' : 'bi-chevron-left'" />
      </button>
    </header>

    <!-- Conteúdo Principal -->
    <div class="sidebar-content custom-scrollbar">
      
      <!-- Camadas Base -->
      <section class="category-block" :class="{ 'is-open': openBase }">
        <button
          class="category-header btn-reset"
          :aria-expanded="openBase"
          aria-controls="base-layers-content"
          @click="toggleBase"
        >
          <span class="cat-dot bg-secondary" aria-hidden="true" />
          <i class="bi bi-map cat-icon" aria-hidden="true" />
          <span class="cat-label" v-show="!isCollapsed">Camadas Base</span>
          
          <div class="cat-meta" v-show="!isCollapsed">
            <span class="badge rounded-pill bg-accent-dim text-accent me-1">1</span>
            <span class="text-muted small">{{ store.availableBaseLayers.length }}</span>
            <i class="bi bi-chevron-down cat-chevron ms-2" :class="{ 'is-rotated': openBase }" />
          </div>
        </button>

        <div 
          id="base-layers-content" 
          class="category-body" 
          v-show="openBase && !isCollapsed"
        >
          <div class="category-body-inner">
            <LayerCard
              v-for="layer in store.availableBaseLayers"
              :key="layer.key"
              type="base"
              :layer-key="layer.key"
              :label="layer.label"
              :meta="layer.meta"
              :collapsed="isCollapsed"
            />
          </div>
        </div>
      </section>

      <!-- Divisor Temático -->
      <div class="section-divider" v-show="!isCollapsed">
        <span class="divider-text">Análise Temática</span>
        <span class="badge border border-secondary text-muted">{{ store.availableOverlays.length }}</span>
      </div>

      <!-- Categorias de Overlay -->
      <section
        v-for="cat in categoriesList"
        :key="cat.key"
        class="category-block"
        :class="{ 'is-open': openCategories[cat.key] }"
      >
        <button
          class="category-header btn-reset"
          :aria-expanded="openCategories[cat.key]"
          :aria-controls="`cat-content-${cat.key}`"
          @click="toggleCategory(cat.key)"
        >
          <span class="cat-dot" :style="{ background: cat.color }" aria-hidden="true" />
          <i class="bi cat-icon" :class="cat.icon" aria-hidden="true" />
          <span class="cat-label" v-show="!isCollapsed">{{ cat.label }}</span>

          <div class="cat-meta" v-show="!isCollapsed">
            <span
              v-if="visibleCount(cat.key) > 0"
              class="badge rounded-pill bg-accent-dim text-accent me-1"
            >
              {{ visibleCount(cat.key) }}
            </span>
            <span class="text-muted small">{{ cat.layerList.length }}</span>
            <i class="bi bi-chevron-down cat-chevron ms-2" :class="{ 'is-rotated': openCategories[cat.key] }" />
          </div>
        </button>

        <div 
          :id="`cat-content-${cat.key}`" 
          class="category-body" 
          v-show="openCategories[cat.key] && !isCollapsed"
        >
          <div class="category-body-inner">
            <LayerCard
              v-for="layer in cat.layerList"
              :key="layer.key"
              type="overlay"
              :layer-key="layer.key"
              :label="layer.label"
              :meta="layer.meta"
              :legend="layer.legend ?? null"
              :search-fields="layer.searchFields ?? []"
              :collapsed="isCollapsed"
            />
          </div>
        </div>
      </section>
    </div>

    <!-- Rodapé -->
    <footer class="sidebar-footer">
      <i class="bi bi-hdd-network-fill text-accent" aria-hidden="true" />
      <span v-show="!isCollapsed" class="ms-2">EPSG:4326 | Online</span>
    </footer>
  </aside>
</template>

<style scoped>
/* Variáveis de Tema (Devem estar no main.css ou :root) */
:root {
  --sidebar-w: 280px;
  --sidebar-collapsed-w: 64px;
  --bg-sidebar: #0f172a;
  --border-color: rgba(255, 255, 255, 0.1);
  --text-main: #f8fafc;
  --text-muted: #94a3b8;
  --text-dim: #64748b;
  --accent: #00d4aa;
  --bg-accent-dim: rgba(0, 212, 170, 0.1);
  --transition-speed: 0.3s;
}

#sidebar {
  width: var(--sidebar-w);
  background: var(--bg-sidebar);
  border-right: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  transition: width var(--transition-speed) ease-in-out;
  height: 100vh;
  z-index: 1050;
  box-shadow: 4px 0 10px rgba(0, 0, 0, 0.3);
}

#sidebar.is-collapsed {
  width: var(--sidebar-collapsed-w);
}

/* Header */
.sidebar-header {
  height: 64px;
  padding: 0 16px;
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
  overflow: hidden;
}

.brand-logo {
  width: 32px;
  height: 32px;
  background: linear-gradient(135deg, var(--accent), #3b82f6);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #0f172a;
  font-size: 1.2rem;
}

.brand-name {
  font-weight: 700;
  font-size: 1.1rem;
  color: var(--text-main);
  white-space: nowrap;
}

.brand-accent { color: var(--accent); }

.toggle-btn {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--border-color);
  color: var(--text-muted);
  width: 32px;
  height: 32px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.toggle-btn:hover {
  background: var(--accent);
  color: #0f172a;
}

/* Content */
.sidebar-content {
  flex: 1;
  overflow-y: auto;
  padding: 12px 0;
}

.section-divider {
  padding: 24px 16px 8px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 0.7rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 1px;
  color: var(--text-dim);
}

/* Category Blocks */
.category-block {
  margin: 4px 8px;
}

.category-header {
  width: 100%;
  display: flex;
  align-items: center;
  padding: 10px 12px;
  border-radius: 8px;
  color: var(--text-muted);
  transition: background 0.2s;
}

.category-header:hover {
  background: rgba(255, 255, 255, 0.05);
  color: var(--text-main);
}

.cat-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-right: 12px;
}

.cat-icon {
  font-size: 1rem;
  margin-right: 12px;
}

.cat-label {
  flex: 1;
  font-size: 0.85rem;
  font-weight: 600;
  text-align: left;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.cat-meta {
  display: flex;
  align-items: center;
}

.cat-chevron {
  font-size: 0.8rem;
  transition: transform 0.3s;
}

.cat-chevron.is-rotated {
  transform: rotate(-180deg);
}

/* Body */
.category-body {
  padding-top: 4px;
}

.category-body-inner {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

/* Footer */
.sidebar-footer {
  padding: 16px;
  border-top: 1px solid var(--border-color);
  font-size: 0.75rem;
  color: var(--text-dim);
  display: flex;
  align-items: center;
  background: rgba(0, 0, 0, 0.2);
}

/* Helpers */
.btn-reset {
  background: none;
  border: none;
  padding: 0;
  cursor: pointer;
}

.bg-accent-dim { background: var(--bg-accent-dim); }
.text-accent { color: var(--accent); }

.custom-scrollbar::-webkit-scrollbar { width: 4px; }
.custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: var(--border-color); border-radius: 10px; }
</style>
