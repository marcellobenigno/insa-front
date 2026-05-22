<script setup>
import { ref, computed } from 'vue'
import { useMapStore } from '@/stores/mapStore'
import { OVERLAY_CATEGORIES } from '@/config/layers'
import LayerCard from './LayerCard.vue'

const store = useMapStore()
const isCollapsed = ref(false)

// Accordion das camadas base (inicia colapsado)
const openBase = ref(false)

// Todas as categorias de overlay iniciam colapsadas
const openCategories = ref(
  Object.fromEntries(
    Object.keys(OVERLAY_CATEGORIES).map((key) => [key, false])
  )
)

function toggle() {
  isCollapsed.value = !isCollapsed.value
  // Colapsa todos os accordions quando a sidebar fecha
  if (isCollapsed.value) {
    openBase.value = false
    Object.keys(openCategories.value).forEach(k => (openCategories.value[k] = false))
  }
}

function toggleBase() {
  openBase.value = !openBase.value
}

function toggleCategory(key) {
  openCategories.value[key] = !openCategories.value[key]
}

// Conta camadas visíveis por categoria para feedback visual no badge
function visibleCount(categoryKey) {
  const layers = OVERLAY_CATEGORIES[categoryKey].layers
  return Object.keys(layers).filter(k => store.visibleOverlays[k]).length
}

// Lista de categorias como array para o v-for
const categories = computed(() =>
  Object.entries(OVERLAY_CATEGORIES).map(([key, cat]) => ({
    key,
    ...cat,
    layerList: Object.entries(cat.layers).map(([lKey, l]) => ({ key: lKey, ...l })),
  }))
)
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

      <!-- ── Camadas Base (accordion) ── -->
      <div class="category-block" :class="{ open: openBase }">
        <button
          class="category-header"
          :title="openBase ? 'Recolher' : 'Expandir'"
          @click="toggleBase"
        >
          <span class="cat-dot" style="background: #94a3b8" />
          <i class="bi bi-map cat-icon" />
          <span class="cat-label">Camadas Base</span>
          <span
            class="cat-active-badge"
            title="1 camada base ativa"
          >1</span>
          <span class="cat-count">{{ store.availableBaseLayers.length }}</span>
          <i
            class="bi bi-chevron-down cat-chevron"
            :class="{ rotated: openBase }"
          />
        </button>

        <div class="category-body">
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
      </div>

      <!-- ── Análise Temática (agrupada por categoria) ── -->
      <div class="section-title section-title--gap">
        <span>Análise Temática</span>
        <span class="count-badge">{{ store.availableOverlays.length }}</span>
      </div>

      <div
        v-for="cat in categories"
        :key="cat.key"
        class="category-block"
        :class="{ open: openCategories[cat.key] }"
      >
        <!-- Cabeçalho da categoria (accordion trigger) -->
        <button
          class="category-header"
          :title="openCategories[cat.key] ? 'Recolher' : 'Expandir'"
          @click="toggleCategory(cat.key)"
        >
          <span class="cat-dot" :style="{ background: cat.color }" />

          <i class="bi cat-icon" :class="cat.icon" />

          <span class="cat-label">{{ cat.label }}</span>

          <span
            v-if="visibleCount(cat.key) > 0"
            class="cat-active-badge"
            :title="`${visibleCount(cat.key)} camada(s) visível(eis)`"
          >
            {{ visibleCount(cat.key) }}
          </span>

          <span class="cat-count">{{ cat.layerList.length }}</span>

          <i
            class="bi bi-chevron-down cat-chevron"
            :class="{ rotated: openCategories[cat.key] }"
          />
        </button>

        <!-- Camadas da categoria (accordion body) -->
        <div class="category-body">
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

      </div>

    </div>

    <!-- Rodapé -->
    <div class="sidebar-footer">
      <i class="bi bi-hdd-network-fill footer-icon" />
      <span>EPSG:4326 | Online</span>
    </div>

  </aside>
</template>

<style scoped>
/* ── Layout geral ────────────────────────────────────────────────────────── */
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

/* ── Cabeçalho ───────────────────────────────────────────────────────────── */
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

/* ── Conteúdo com scroll ─────────────────────────────────────────────────── */
.sidebar-content {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 12px 0;
}

.sidebar-content::-webkit-scrollbar {
  width: 5px;
}

.sidebar-content::-webkit-scrollbar-thumb {
  background: var(--border-color);
  border-radius: 10px;
}

/* ── Títulos de seção ────────────────────────────────────────────────────── */
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

/* ── Bloco de categoria (accordion) ─────────────────────────────────────── */
.category-block {
  margin: 0 10px 4px;
}

.category-header {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 7px;
  padding: 8px 10px;
  background: transparent;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  color: var(--text-muted);
  transition: background 0.15s;
  text-align: left;
}

.category-header:hover {
  background: rgba(255, 255, 255, 0.04);
}

.cat-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  flex-shrink: 0;
}

.cat-icon {
  font-size: 0.85rem;
  flex-shrink: 0;
  color: var(--text-dim);
}

.cat-label {
  flex: 1;
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--text-muted);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* badge verde indicando quantas camadas estão ativas na categoria */
.cat-active-badge {
  font-size: 0.6rem;
  font-weight: 700;
  background: rgba(0, 212, 170, 0.15);
  color: var(--accent);
  border-radius: 20px;
  padding: 1px 6px;
  line-height: 1.6;
  flex-shrink: 0;
}

.cat-count {
  font-size: 0.6rem;
  border: 1px solid var(--border-color);
  border-radius: 20px;
  padding: 1px 6px;
  color: var(--text-dim);
  flex-shrink: 0;
}

.cat-chevron {
  font-size: 0.72rem;
  color: var(--text-dim);
  transition: transform 0.22s var(--transition-curve);
  flex-shrink: 0;
}

.cat-chevron.rotated {
  transform: rotate(-180deg);
}

/* Accordion body – animado via grid-template-rows */
.category-body {
  display: grid;
  grid-template-rows: 0fr;
  transition: grid-template-rows 0.25s var(--transition-curve);
}

.category-block.open .category-body {
  grid-template-rows: 1fr;
}

.category-body-inner {
  overflow: hidden;
  display: flex;
  flex-direction: column;
  gap: 0; /* LayerCard já tem margin própria */
}

/* Quando a sidebar colapsa, oculta todos os textos dos cards */
#sidebar.collapsed :deep(.layer-info),
#sidebar.collapsed :deep(.layer-actions-top) {
  display: none;
}

/* Oculta labels de categoria quando colapsado */
#sidebar.collapsed .cat-label,
#sidebar.collapsed .cat-count,
#sidebar.collapsed .cat-active-badge,
#sidebar.collapsed .cat-chevron,
#sidebar.collapsed .cat-icon {
  display: none;
}

/* ── Rodapé ──────────────────────────────────────────────────────────────── */
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