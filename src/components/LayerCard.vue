<template>
  <div class="layer-card">
    <div class="layer-main-row">

      <button
        class="layer-icon-btn"
        :class="{ active: isVisible }"
        :title="isVisible ? 'Ocultar' : 'Exibir'"
        @click="toggleVisibility"
      >
        <i class="bi" :class="isVisible ? 'bi-eye-fill' : 'bi-eye-slash'" />
      </button>

      <div class="layer-info">
        <span class="layer-label">{{ label }}</span>
        <span class="layer-meta">{{ meta }}</span>
      </div>

      <div class="layer-actions-top">

        <button
          class="action-btn"
          :class="{ active: activePanel === 'opacity' }"
          title="Opacidade"
          @click="togglePanel('opacity')"
        >
          <i class="bi bi-sliders" />
        </button>

        <template v-if="type === 'overlay'">
          <button
            v-if="legend"
            class="action-btn"
            :class="{ active: activePanel === 'legend' }"
            title="Legenda"
            @click="togglePanel('legend')"
          >
            <i class="bi bi-palette" />
          </button>
          <button
            v-if="searchFields.length > 0"
            class="action-btn"
            :class="{ active: activePanel === 'search' }"
            title="Busca"
            @click="togglePanel('search')"
          >
            <i class="bi bi-search" />
          </button>
        </template>

      </div>
    </div>

    <div class="sub-panel" :class="{ open: activePanel === 'opacity' }">
      <div class="sub-panel-inner">
        <div class="panel-title">
          <i class="bi bi-sliders" />
          Opacidade: <span>{{ Math.round(opacity * 100) }}%</span>
        </div>
        <input
          type="range"
          class="custom-range"
          min="0"
          max="100"
          :value="Math.round(opacity * 100)"
          @input="onOpacityInput"
        />
      </div>
    </div>

    <div class="sub-panel" :class="{ open: activePanel === 'legend' }">
      <div class="sub-panel-inner">
        <div class="panel-title"><i class="bi bi-palette" /> Legenda</div>
        <img v-if="legend" :src="legend" alt="Legenda da camada" class="legend-img" />
      </div>
    </div>

    <div class="sub-panel" :class="{ open: activePanel === 'search' }">
      <div class="sub-panel-inner">
        <div class="search-box">
          <select
            v-if="searchFields.length > 1"
            v-model="selectedField"
            class="search-input"
          >
            <option v-for="f in searchFields" :key="f" :value="f">{{ f }}</option>
          </select>
          <input
            v-model="searchQuery"
            type="text"
            class="search-input"
            :placeholder="`Buscar por ${selectedField || 'campo'}…`"
          />
          <button class="search-btn">Filtrar Mapa</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useMapStore } from '@/stores/mapStore'

const props = defineProps({
  layerKey:     { type: String,  required: true },
  type:         { type: String,  required: true }, // 'base' | 'overlay'
  label:        { type: String,  required: true },
  meta:         { type: String,  default: '' },
  legend:       { type: String,  default: null },
  searchFields: { type: Array,   default: () => [] },
  collapsed:    { type: Boolean, default: false },
})

const store = useMapStore()

const isVisible = computed(() =>
  props.type === 'base'
    ? store.activeBaseLayerKey === props.layerKey
    : store.visibleOverlays[props.layerKey],
)

// Busca dinamicamente a opacidade da store usando a chave única da camada
const opacity = computed(() => store.layerOpacity[props.layerKey] ?? 1)

const activePanel = ref(null)
const searchQuery  = ref('')
const selectedField = ref(props.searchFields[0] ?? '')

watch(
  () => props.collapsed,
  (val) => { if (val) activePanel.value = null },
)

function toggleVisibility() {
  if (props.type === 'base') store.setBaseLayer(props.layerKey)
  else store.toggleOverlay(props.layerKey)
}

function togglePanel(name) {
  activePanel.value = activePanel.value === name ? null : name
}

function onOpacityInput(e) {
  store.setLayerOpacity(props.layerKey, Number(e.target.value) / 100)
}
</script>

<style scoped>
.layer-card {
  margin: 3px 10px 6px;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 10px;
  transition: all 0.2s;
  overflow: hidden;
}

.layer-card:hover {
  border-color: rgba(0, 212, 170, 0.3);
  background: var(--bg-card-hover);
}

.layer-main-row {
  padding: 8px 10px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.layer-icon-btn {
  width: 28px;
  height: 28px;
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.03);
  border: none;
  color: var(--text-muted);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
  flex-shrink: 0;
  font-size: 0.85rem;
}

.layer-icon-btn.active {
  color: var(--accent);
  background: var(--bg-accent-dim);
}

.layer-info {
  flex: 1;
  min-width: 0;
}

/* Label legível: até 2 linhas, sem ellipsis prematuro */
.layer-label {
  display: block;
  font-size: 0.78rem;
  font-weight: 600;
  line-height: 1.3;
  white-space: normal;
  overflow-wrap: break-word;
  color: var(--text-main);
}

.layer-meta {
  font-size: 0.65rem;
  color: var(--text-dim);
  margin-top: 1px;
}

/* Ações empilhadas verticalmente para não roubar largura do label */
.layer-actions-top {
  display: flex;
  flex-direction: column;
  gap: 3px;
  flex-shrink: 0;
}

.action-btn {
  width: 24px;
  height: 24px;
  border-radius: 5px;
  border: 1px solid transparent;
  background: transparent;
  color: var(--text-dim);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.78rem;
  cursor: pointer;
  transition: all 0.2s;
}

.action-btn:hover {
  background: rgba(255, 255, 255, 0.05);
  color: var(--text-main);
}

.action-btn.active {
  color: var(--accent-secondary);
  background: rgba(59, 130, 246, 0.1);
  border-color: rgba(59, 130, 246, 0.2);
}

.sub-panel {
  display: grid;
  grid-template-rows: 0fr;
  transition: grid-template-rows 0.25s ease;
  background: rgba(0, 0, 0, 0.2);
  border-top: 1px solid transparent;
  transition:
    grid-template-rows 0.25s ease,
    border-top-color   0.25s ease;
}

.sub-panel.open {
  grid-template-rows: 1fr;
  border-top-color: var(--border-color);
}

.sub-panel-inner {
  overflow: hidden;
  padding: 0 12px;
  transition: padding 0.25s ease;
}

.sub-panel.open .sub-panel-inner {
  padding: 12px;
}

.panel-title {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--text-muted);
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.custom-range {
  width: 100%;
  accent-color: var(--accent);
}

.legend-img {
  max-width: 100%;
  border-radius: 4px;
  background: rgba(255, 255, 255, 0.05);
  padding: 4px;
}

.search-box {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.search-input {
  background: var(--bg-app);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  padding: 6px 10px;
  color: var(--text-main);
  font-size: 0.8rem;
  width: 100%;
}

.search-input:focus {
  outline: none;
  border-color: var(--accent-secondary);
}

.search-btn {
  background: var(--accent-secondary);
  color: white;
  border: none;
  border-radius: 6px;
  padding: 6px;
  font-size: 0.8rem;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.2s;
}

.search-btn:hover {
  opacity: 0.85;
}
</style>