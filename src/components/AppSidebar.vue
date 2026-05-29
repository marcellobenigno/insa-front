<script setup>
import { ref, computed } from 'vue'
import { useMapStore } from '@/stores/mapStore'
import { useSidebar } from '@/composables/useSidebar'
import { useTheme } from '@/composables/useTheme'
import LayerCard from './LayerCard.vue'
import GeoSearch from './GeoSearch.vue'

const store = useMapStore()
const { isCollapsed, openBase, openCategories, toggleSidebar, toggleBase, toggleCategory } = useSidebar()
const { isDark, toggleTheme } = useTheme()

function clearAllAndCollapse() {
  store.clearAllOverlays()
  Object.keys(openCategories).forEach(k => { openCategories[k] = false })
}

// Conta camadas visíveis por categoria para feedback visual no badge
function visibleCount(categoryKey) {
  const cat = store.availableCategories.find(c => c.key === categoryKey)
  return cat ? cat.layers.filter(l => l.visible).length : 0
}

// ── Filtro de camadas ──────────────────────────────────────────────────────────
const searchTerm = ref('')

const filteredCategories = computed(() => {
  if (!searchTerm.value.trim()) return store.availableCategories
  const q = searchTerm.value.trim().toLowerCase()
  return store.availableCategories
    .map(cat => ({
      ...cat,
      layers: cat.layers.filter(l => l.label.toLowerCase().includes(q)),
    }))
    .filter(cat => cat.layers.length > 0)
})

const filteredLayerCount = computed(() =>
  filteredCategories.value.reduce((sum, cat) => sum + cat.layers.length, 0)
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
      <div class="header-actions">
        <button
          class="toggle-btn"
          :title="isDark ? 'Mudar para tema claro' : 'Mudar para tema escuro'"
          :aria-label="isDark ? 'Ativar tema claro' : 'Ativar tema escuro'"
          @click="toggleTheme"
        >
          <i class="bi" :class="isDark ? 'bi-sun' : 'bi-moon-stars'" />
        </button>
        <button
          class="toggle-btn"
          :title="isCollapsed ? 'Expandir Sidebar' : 'Recolher Sidebar'"
          :aria-label="isCollapsed ? 'Expandir painel lateral' : 'Recolher painel lateral'"
          :aria-expanded="!isCollapsed"
          @click="toggleSidebar"
        >
          <i class="bi" :class="isCollapsed ? 'bi-chevron-right' : 'bi-chevron-left'" />
        </button>
      </div>
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
        <div class="divider-actions">
          <span class="badge overlay-count-badge" :class="{ 'is-filtered': searchTerm }">
            <template v-if="searchTerm">{{ filteredLayerCount }} de </template>{{ store.availableOverlays.length }}
          </span>
          <Transition name="clear-btn">
            <button
              v-if="store.activeOverlayCount > 0"
              class="clear-overlays-btn"
              title="Limpar camadas ativas"
              aria-label="Desligar todas as camadas de sobreposição"
              @click="clearAllAndCollapse()"
            >
              <i class="bi bi-x-circle" aria-hidden="true" />
              <span class="clear-overlays-label">Limpar</span>
            </button>
          </Transition>
        </div>
      </div>

      <!-- Filtro de camadas -->
      <div class="layer-search-box" v-show="!isCollapsed" role="search">
        <i class="bi bi-search layer-search-icon" aria-hidden="true" />
        <input
          v-model="searchTerm"
          type="text"
          class="layer-search-input"
          placeholder="Filtrar camadas por nome"
          aria-label="Filtrar camadas"
        />
        <button
          v-if="searchTerm"
          class="layer-search-clear"
          aria-label="Limpar busca"
          @click="searchTerm = ''"
        >
          <i class="bi bi-x" aria-hidden="true" />
        </button>
      </div>

      <!-- Categorias de Overlay -->
      <section
        v-for="cat in filteredCategories"
        :key="cat.key"
        class="category-block"
        :class="{ 'is-open': searchTerm || openCategories[cat.key] }"
      >
        <button
          class="category-header btn-reset"
          :aria-expanded="searchTerm ? true : openCategories[cat.key]"
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
            <i class="bi bi-chevron-down cat-chevron ms-2" :class="{ 'is-rotated': searchTerm || openCategories[cat.key] }" />
          </div>
        </button>

        <div
          :id="`cat-content-${cat.key}`"
          class="category-body"
          v-show="(searchTerm || openCategories[cat.key]) && !isCollapsed"
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

    <!-- Rodapé / Busca Geoespacial -->
    <GeoSearch />
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

@media (max-width: 768px) {
  #sidebar {
    position: fixed;
    top: 0;
    left: 0;
    width: var(--sidebar-mobile-w);
    z-index: 1100;
    transform: translateX(0);
    transition: transform var(--transition-speed) ease-in-out;
  }

  #sidebar.is-collapsed {
    width: var(--sidebar-mobile-w);
    transform: translateX(-100%);
  }
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

.header-actions {
  display: flex;
  align-items: center;
  gap: 6px;
}

.toggle-btn {
  width: 32px;
  height: 32px;
  border-radius: 6px;
  border: 1px solid var(--border-color);
  background: var(--btn-bg);
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
  margin: 6px;
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
  background: var(--hover-overlay);
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
  font-size: 0.93rem;
  font-weight: 700;
  color: var(--text-main);
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

/* ── Reset de botão ──────────────────────────────────────────────────────────── */
.btn-reset {
  background: none;
  border: none;
  padding: 0;
  cursor: pointer;
}

/* ── Filtro de camadas ───────────────────────────────────────────────────────── */
.layer-search-box {
  position: relative;
  display: flex;
  align-items: center;
  margin: 0 10px 10px;
}

.layer-search-icon {
  position: absolute;
  left: 10px;
  font-size: 0.8rem;
  color: var(--text-muted);
  pointer-events: none;
}

.layer-search-input {
  width: 100%;
  padding: 6px 32px 6px 30px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  color: var(--text-main);
  font-size: 0.8rem;
  outline: none;
  transition: border-color 0.2s;
}

.layer-search-input::placeholder { color: var(--text-muted); }

.layer-search-input:focus { border-color: var(--accent); }

.layer-search-clear {
  position: absolute;
  right: 6px;
  border: none;
  background: none;
  color: var(--text-muted);
  cursor: pointer;
  padding: 2px 4px;
  line-height: 1;
  border-radius: 4px;
  transition: color 0.2s;
}

.layer-search-clear:hover { color: var(--text-main); }

/* ── Badge de contagem de camadas ────────────────────────────────────────────── */
.overlay-count-badge {
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: var(--text-main);
  background: rgba(255, 255, 255, 0.08);
  font-size: 0.7rem;
  font-weight: 600;
}

.overlay-count-badge.is-filtered {
  border-color: var(--accent);
  color: var(--accent);
  background: var(--bg-accent-dim);
}

/* ── Limpar camadas ──────────────────────────────────────────────────────────── */
.divider-actions {
  display: flex;
  align-items: center;
  gap: 6px;
}

.clear-overlays-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 2px 7px 2px 5px;
  border: 1px solid rgba(255, 80, 80, 0.35);
  border-radius: 10px;
  background: rgba(255, 80, 80, 0.08);
  color: rgba(255, 120, 120, 0.85);
  font-size: 0.7rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s, color 0.2s, border-color 0.2s;
  white-space: nowrap;
}

.clear-overlays-btn:hover {
  background: rgba(255, 80, 80, 0.22);
  border-color: rgba(255, 80, 80, 0.7);
  color: #ff8080;
}

.clear-overlays-btn .bi {
  font-size: 0.75rem;
}

.clear-btn-enter-active,
.clear-btn-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.clear-btn-enter-from,
.clear-btn-leave-to {
  opacity: 0;
  transform: scale(0.8);
}
</style>
