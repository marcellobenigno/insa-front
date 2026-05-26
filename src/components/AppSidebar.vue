<script setup>
import { useMapStore } from '@/stores/mapStore'
import { useSidebar } from '@/composables/useSidebar'
import LayerCard from './LayerCard.vue'

const store = useMapStore()
const { isCollapsed, openBase, openCategories, toggleSidebar, toggleBase, toggleCategory } = useSidebar()

// Conta camadas visíveis por categoria para feedback visual no badge
function visibleCount(categoryKey) {
  const cat = store.availableCategories.find(c => c.key === categoryKey)
  return cat ? cat.layers.filter(l => l.visible).length : 0
}
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
        v-for="cat in store.availableCategories"
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
            <span class="text-muted small">{{ cat.layers.length }}</span>
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
              v-for="layer in cat.layers"
              :key="layer.key"
              type="overlay"
              :layer-key="layer.key"
              :label="layer.label"
              :meta="layer.meta"
              :legend="layer.legend ?? null"
              :search-fields="layer.searchFields ?? []"
              :field-types="layer.fieldTypes ?? {}"
              :desc-fields="layer.descFields ?? {}"
              :collapsed="isCollapsed"
            />
          </div>
        </div>
      </section>
    </div>

    <!-- Rodapé -->
    <footer class="sidebar-footer">
      <i class="bi bi-hdd-network-fill text-accent" aria-hidden="true" />
    </footer>
  </aside>
</template>

<style scoped>
/* ── Sidebar ─────────────────────────────────────────────────────────────────── */
#sidebar {
  width: var(--sidebar-w);
  height: 100vh;
  z-index: 1050;
  display: flex;
  flex-direction: column;
  background: var(--bg-sidebar);
  border-right: 1px solid var(--border-color);
  box-shadow: 4px 0 10px rgba(0, 0, 0, 0.3);
  transition: width var(--transition-speed) ease-in-out;
}

#sidebar.is-collapsed {
  width: var(--sidebar-collapsed-w);
}

/* ── Header ──────────────────────────────────────────────────────────────────── */
.sidebar-header {
  height: 64px;
  padding: 0 16px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid var(--border-color);
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
  font-size: 1.2rem;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, var(--accent), var(--accent-secondary));
  color: var(--text-on-accent);
}

.brand-name {
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--text-main);
  white-space: nowrap;
}

.brand-accent { color: var(--accent); }

.toggle-btn {
  width: 32px;
  height: 32px;
  border-radius: 6px;
  border: 1px solid var(--border-color);
  background: rgba(255, 255, 255, 0.05);
  color: var(--text-muted);
  cursor: pointer;
  transition: background 0.2s, color 0.2s;
}

.toggle-btn:hover {
  background: var(--accent);
  color: var(--text-on-accent);
}

/* ── Conteúdo ────────────────────────────────────────────────────────────────── */
.sidebar-content {
  flex: 1;
  overflow-y: auto;
  padding: 12px 0;
}

.sidebar-content::-webkit-scrollbar       { width: 4px; }
.sidebar-content::-webkit-scrollbar-track  { background: transparent; }
.sidebar-content::-webkit-scrollbar-thumb  { background: var(--border-color); border-radius: 10px; }

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

/* ── Categorias ──────────────────────────────────────────────────────────────── */
.category-block {
  margin: 4px 8px;
}

.category-header {
  width: 100%;
  padding: 10px 12px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  color: var(--text-muted);
  transition: background 0.2s, color 0.2s;
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
  flex-shrink: 0;
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
  transition: transform var(--transition-speed);
}

.cat-chevron.is-rotated {
  transform: rotate(-180deg);
}

.category-body {
  padding-top: 4px;
}

.category-body-inner {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

/* ── Footer ──────────────────────────────────────────────────────────────────── */
.sidebar-footer {
  padding: 16px;
  display: flex;
  align-items: center;
  font-size: 0.75rem;
  color: var(--text-dim);
  border-top: 1px solid var(--border-color);
  background: rgba(0, 0, 0, 0.2);
}

/* ── Reset de botão ──────────────────────────────────────────────────────────── */
.btn-reset {
  background: none;
  border: none;
  padding: 0;
  cursor: pointer;
}
</style>
