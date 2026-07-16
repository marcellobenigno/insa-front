<script setup>
import { ref, computed } from 'vue'
import { useMapStore } from '@/stores/mapStore'
import { useSidebar } from '@/composables/useSidebar'
import LayerCard from './LayerCard.vue'
import SidebarTreeGroup from './SidebarTreeGroup.vue'
import GeoSearch from './GeoSearch.vue'

const store = useMapStore()
const { isCollapsed, openBase, openCategories, toggleSidebar, toggleBase } = useSidebar()

function clearAllAndCollapse() {
  store.clearAllOverlays()
  Object.keys(openCategories).forEach((k) => {
    openCategories[k] = false
  })
}

// ── Filtro de camadas ──────────────────────────────────────────────────────────
const searchTerm = ref('')

function normalize(s) {
  return s.normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase()
}

// Poda recursivamente a árvore mantendo só folhas cujo label bate com a busca
// (e os grupos ancestrais que têm ao menos uma folha correspondente).
function filterNode(node, q) {
  if (node.layer) {
    return normalize(node.layer.label).includes(q) ? node : null
  }
  const children = (node.children ?? []).map((child) => filterNode(child, q)).filter(Boolean)
  return children.length > 0 ? { ...node, children } : null
}

function countLeaves(nodes) {
  let total = 0
  for (const node of nodes) {
    total += node.layer ? 1 : countLeaves(node.children ?? [])
  }
  return total
}

const filteredTree = computed(() => {
  if (!searchTerm.value.trim()) return store.availableTree
  const q = normalize(searchTerm.value.trim())
  return store.availableTree.map((node) => filterNode(node, q)).filter(Boolean)
})

const filteredLayerCount = computed(() => countLeaves(filteredTree.value))

function handleBaseClick() {
  if (isCollapsed.value) {
    toggleSidebar()
    if (!openBase.value) toggleBase()
  } else {
    toggleBase()
  }
}
</script>

<template>
  <aside
    id="sidebar"
    :class="{ 'is-collapsed': isCollapsed }"
    role="complementary"
    aria-label="Painel de Controle do Mapa"
  >
    <!-- Conteúdo Principal -->
    <div class="sidebar-content custom-scrollbar">
      <!-- Camadas Base -->
      <section class="category-block" :class="{ 'is-open': openBase }">
        <button
          class="category-header btn-reset"
          :aria-expanded="openBase"
          aria-controls="base-layers-content"
          @click="handleBaseClick"
        >
          <i class="bi bi-globe cat-icon" aria-hidden="true" />
          <span class="cat-label" v-show="!isCollapsed">Camadas Base</span>

          <div class="cat-meta" v-show="!isCollapsed">
            <span class="cat-badge me-1">1</span>
            <span class="cat-count">{{ store.availableBaseLayers.length }}</span>
            <i class="bi bi-chevron-down cat-chevron ms-2" :class="{ 'is-rotated': openBase }" />
          </div>
        </button>

        <div id="base-layers-content" class="category-body" v-show="openBase && !isCollapsed">
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
          <span v-if="store.activeOverlayCount > 0" class="cat-badge me-1">{{
            store.activeOverlayCount
          }}</span>
          <span class="cat-count">
            <template v-if="searchTerm">{{ filteredLayerCount }} de </template
            >{{ store.availableOverlays.length }}
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

      <!-- Árvore hierárquica de camadas de sobreposição -->
      <SidebarTreeGroup
        v-for="node in filteredTree"
        :key="node.key"
        :node="node"
        :depth="0"
        :force-open="!!searchTerm"
      />
    </div>

    <!-- Rodapé / Busca Geoespacial -->
    <GeoSearch />
  </aside>
</template>

<style scoped>
/* ── Sidebar ─────────────────────────────────────────────────────────────────── */
#sidebar {
  width: var(--sidebar-w);
  height: 100%;
  z-index: 1050;
  display: flex;
  flex-direction: column;
  background: var(--bg-sidebar);
  border-right: 1px solid var(--border-color);
  transition: width var(--transition-speed) ease-in-out;
}

#sidebar.is-collapsed {
  width: var(--sidebar-collapsed-w);
}

/* is-collapsed overrides para .category-block/.category-header/.cat-icon agora vivem em main.css */

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

/* ── Conteúdo ────────────────────────────────────────────────────────────────── */
.sidebar-content {
  flex: 1;
  overflow-y: auto;
  padding: 8px 0;
}

.sidebar-content::-webkit-scrollbar {
  width: 4px;
}
.sidebar-content::-webkit-scrollbar-track {
  background: transparent;
}
.sidebar-content::-webkit-scrollbar-thumb {
  background: var(--border-color);
  border-radius: 10px;
}

.section-divider {
  padding: 20px 16px 6px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  color: var(--text-dim);
}

/* ── Categorias ──────────────────────────────────────────────────────────────── */
/* .category-block / .category-header / .cat-* / .category-body / .btn-reset     */
/* agora vivem em src/assets/main.css (compartilhado com SidebarTreeGroup.vue)   */

/* ── Filtro de camadas ───────────────────────────────────────────────────────── */
.layer-search-box {
  position: relative;
  display: flex;
  align-items: center;
  margin: 0 10px 8px;
}

.layer-search-icon {
  position: absolute;
  left: 12px;
  font-size: 12px;
  color: var(--text-dim);
  pointer-events: none;
}

.layer-search-input {
  width: 100%;
  padding: 7px 30px 7px 32px;
  background: var(--btn-bg);
  border: 1px solid var(--border-color);
  border-radius: 9999px;
  color: var(--text-main);
  font-size: 13px;
  outline: none;
  transition:
    border-color 0.15s,
    box-shadow 0.15s;
}

.layer-search-input::placeholder {
  color: var(--text-dim);
}

.layer-search-input:focus {
  border-color: var(--accent);
  box-shadow: 0 0 0 3px var(--bg-accent-dim);
}

.layer-search-clear {
  position: absolute;
  right: 8px;
  border: none;
  background: none;
  color: var(--text-dim);
  cursor: pointer;
  padding: 2px;
  width: 18px;
  height: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  font-size: 13px;
  transition: color 0.15s;
}

.layer-search-clear:hover {
  color: var(--text-main);
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
  padding: 2px 8px 2px 6px;
  border: 1px solid rgba(255, 59, 48, 0.3);
  border-radius: 9999px;
  background: rgba(255, 59, 48, 0.06);
  color: rgba(255, 59, 48, 0.85);
  font-size: 11px;
  font-weight: 600;
  cursor: pointer;
  transition:
    background 0.15s,
    border-color 0.15s,
    color 0.15s;
  white-space: nowrap;
}

.clear-overlays-btn:hover {
  background: rgba(255, 59, 48, 0.12);
  border-color: rgba(255, 59, 48, 0.5);
  color: rgb(255, 59, 48);
}

.clear-overlays-btn:active {
  transform: scale(0.95);
}

.clear-overlays-btn .bi {
  font-size: 11px;
}

.clear-btn-enter-active,
.clear-btn-leave-active {
  transition:
    opacity 0.2s ease,
    transform 0.2s ease;
}

.clear-btn-enter-from,
.clear-btn-leave-to {
  opacity: 0;
  transform: scale(0.85);
}

/* .cat-badge / .cat-count agora vivem em src/assets/main.css */
</style>
