<script setup>
import { ref, computed, watch } from 'vue'
import { useMapStore } from '@/stores/mapStore'
import stylesData from '@/assets/styles.json'

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

// Reatividade da visibilidade
const isVisible = computed(() =>
  props.type === 'base'
    ? store.activeBaseLayerKey === props.layerKey
    : store.visibleOverlays[props.layerKey],
)

// Reatividade da opacidade
const opacity = computed(() => store.layerOpacity[props.layerKey] ?? 1)

const activePanel = ref(null)
const searchQuery  = ref('')
const selectedField = ref(props.searchFields[0] ?? '')

// Fecha painéis se a sidebar colapsar
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

// ── Legenda dinâmica via styles.json ──────────────────────────────────────────

function formatNum(n) {
  // Remove casas decimais desnecessárias (ex: 1.30000000004 → "1.3")
  return parseFloat(n.toFixed(3)).toString()
}

const legendItems = computed(() => {
  const styleEntry = stylesData[props.layerKey]
  if (!styleEntry) return []

  const entries = Object.entries(styleEntry)
  if (entries.length === 0) return []

  // Detecta se as chaves são numéricas
  const isNumeric = entries.every(([key]) => !isNaN(parseFloat(key)) && isFinite(key))

  if (isNumeric) {
    const sorted = entries
      .map(([key, color]) => ({ value: parseFloat(key), color }))
      .sort((a, b) => a.value - b.value)

    return sorted.map((item, i) => {
      const next = sorted[i + 1]
      const label = next
        ? `${formatNum(item.value)} – ${formatNum(next.value)}`
        : `≥ ${formatNum(item.value)}`
      return { label, color: item.color }
    })
  }

  // Categórico: retorna chave como label
  return entries.map(([key, color]) => ({ label: key, color }))
})

const hasLegend = computed(() => legendItems.value.length > 0 || !!props.legend)
</script>

<template>
  <div 
    class="layer-card" 
    :class="{ 'is-active': isVisible }"
  >
    <!-- Linha Principal -->
    <div class="layer-main-row">
      <button
        class="visibility-toggle"
        :class="{ 'is-visible': isVisible }"
        :title="isVisible ? 'Ocultar camada' : 'Exibir camada'"
        :aria-label="isVisible ? `Ocultar ${label}` : `Exibir ${label}`"
        @click="toggleVisibility"
      >
        <i class="bi" :class="isVisible ? 'bi-eye-fill' : 'bi-eye-slash'" aria-hidden="true" />
      </button>

      <div class="layer-info">
        <span class="layer-label">{{ label }}</span>
        <span class="layer-meta" v-if="meta">{{ meta }}</span>
      </div>

      <div class="layer-actions">
        <button
          class="action-btn"
          :class="{ 'is-panel-open': activePanel === 'opacity' }"
          title="Ajustar Opacidade"
          aria-label="Ajustar opacidade"
          @click="togglePanel('opacity')"
        >
          <i class="bi bi-sliders" aria-hidden="true" />
        </button>

        <template v-if="type === 'overlay'">
          <button
            v-if="hasLegend"
            class="action-btn"
            :class="{ 'is-panel-open': activePanel === 'legend' }"
            title="Ver Legenda"
            aria-label="Ver legenda"
            @click="togglePanel('legend')"
          >
            <i class="bi bi-palette" aria-hidden="true" />
          </button>
          
          <button
            v-if="searchFields.length > 0"
            class="action-btn"
            :class="{ 'is-panel-open': activePanel === 'search' }"
            title="Buscar na camada"
            aria-label="Buscar na camada"
            @click="togglePanel('search')"
          >
            <i class="bi bi-search" aria-hidden="true" />
          </button>
        </template>
      </div>
    </div>

    <!-- Painéis Expansíveis (Bootstrap-like Collapse) -->
    <Transition name="panel-fade">
      <div class="layer-sub-panel" v-if="activePanel">
        
        <!-- Painel de Opacidade -->
        <div v-if="activePanel === 'opacity'" class="panel-content">
          <div class="d-flex justify-content-between align-items-center mb-2">
            <label class="panel-label">Opacidade</label>
            <span class="badge bg-dark">{{ Math.round(opacity * 100) }}%</span>
          </div>
          <input
            type="range"
            class="form-range custom-slider"
            min="0"
            max="100"
            :value="Math.round(opacity * 100)"
            @input="onOpacityInput"
          />
        </div>

        <!-- Painel de Legenda -->
        <div v-if="activePanel === 'legend'" class="panel-content">
          <label class="panel-label mb-2">Legenda</label>

          <!-- Legenda dinâmica via styles.json -->
          <div v-if="legendItems.length > 0" class="legend-list">
            <div
              v-for="item in legendItems"
              :key="item.label"
              class="legend-item"
            >
              <span class="legend-swatch" :style="{ background: item.color }" />
              <span class="legend-item-label">{{ item.label }}</span>
            </div>
          </div>

          <!-- Fallback: imagem estática -->
          <div v-else-if="legend" class="legend-container">
            <img :src="legend" :alt="`Legenda de ${label}`" class="img-fluid rounded" />
          </div>
        </div>

        <!-- Painel de Busca -->
        <div v-if="activePanel === 'search'" class="panel-content">
          <label class="panel-label mb-2">Busca Avançada</label>
          <div class="search-form">
            <select
              v-if="searchFields.length > 1"
              v-model="selectedField"
              class="form-select form-select-sm mb-2 bg-dark text-light border-secondary"
            >
              <option v-for="f in searchFields" :key="f" :value="f">{{ f }}</option>
            </select>
            <div class="input-group input-group-sm">
              <input
                v-model="searchQuery"
                type="text"
                class="form-control bg-dark text-light border-secondary"
                :placeholder="`Buscar em ${selectedField}...`"
              />
              <button class="btn btn-primary" type="button">
                <i class="bi bi-search" />
              </button>
            </div>
          </div>
        </div>

      </div>
    </Transition>
  </div>
</template>

<style scoped>
/* ── Card ────────────────────────────────────────────────────────────────────── */
.layer-card {
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid var(--border-color);
  background: rgba(255, 255, 255, 0.03);
  transition: background 0.2s, border-color 0.2s;
}

.layer-card:hover {
  background: rgba(255, 255, 255, 0.06);
  border-color: rgba(255, 255, 255, 0.15);
}

.layer-card.is-active {
  border-left: 3px solid var(--accent);
  background: rgba(255, 255, 255, 0.05);
}

.layer-main-row {
  display: flex;
  align-items: center;
  padding: 10px;
  gap: 12px;
}

/* ── Botão de visibilidade ───────────────────────────────────────────────────── */
.visibility-toggle {
  width: 32px;
  height: 32px;
  border: none;
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.05);
  color: var(--text-dim);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s, color 0.2s;
}

.visibility-toggle:hover {
  background: rgba(255, 255, 255, 0.1);
  color: var(--text-main);
}

.visibility-toggle.is-visible {
  color: var(--accent);
  background: var(--bg-accent-dim);
}

/* ── Info da camada ──────────────────────────────────────────────────────────── */
.layer-info {
  flex: 1;
  min-width: 0;
}

.layer-label {
  display: block;
  font-size: 0.85rem;
  font-weight: 600;
  line-height: 1.2;
  color: var(--text-main);
}

.layer-meta {
  display: block;
  font-size: 0.7rem;
  margin-top: 2px;
  color: var(--text-muted);
}

/* ── Ações ───────────────────────────────────────────────────────────────────── */
.layer-actions {
  display: flex;
  gap: 4px;
}

.action-btn {
  width: 28px;
  height: 28px;
  border: none;
  border-radius: 4px;
  background: transparent;
  color: var(--text-muted);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s, color 0.2s;
}

.action-btn:hover {
  background: rgba(255, 255, 255, 0.08);
  color: var(--text-main);
}

.action-btn.is-panel-open {
  background: var(--accent-secondary);
  color: white;
}

/* ── Painéis expansíveis ─────────────────────────────────────────────────────── */
.layer-sub-panel {
  border-top: 1px solid rgba(255, 255, 255, 0.05);
  background: rgba(0, 0, 0, 0.2);
}

.panel-content {
  padding: 12px;
}

.panel-label {
  margin: 0;
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  color: var(--text-dim);
}

.custom-slider {
  accent-color: var(--accent);
}

/* ── Legenda dinâmica ────────────────────────────────────────────────────────── */
.legend-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
  max-height: 220px;
  overflow-y: auto;
  padding-right: 4px;
  scrollbar-width: thin;
  scrollbar-color: rgba(255, 255, 255, 0.15) transparent;
}

.legend-list::-webkit-scrollbar       { width: 4px; }
.legend-list::-webkit-scrollbar-track  { background: transparent; }
.legend-list::-webkit-scrollbar-thumb  { background: rgba(255, 255, 255, 0.15); border-radius: 2px; }

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.legend-swatch {
  flex-shrink: 0;
  width: 22px;
  height: 14px;
  border-radius: 3px;
  border: 1px solid rgba(255, 255, 255, 0.15);
}

.legend-item-label {
  font-size: 0.72rem;
  line-height: 1.3;
  word-break: break-word;
  color: var(--text-muted);
}

/* ── Legenda estática (imagem) ───────────────────────────────────────────────── */
.legend-container {
  padding: 8px;
  border-radius: 4px;
  background: rgba(255, 255, 255, 0.05);
}

/* ── Transição de painel ─────────────────────────────────────────────────────── */
.panel-fade-enter-active,
.panel-fade-leave-active {
  max-height: 300px;
  transition: opacity 0.25s ease, max-height 0.25s ease, transform 0.25s ease;
}

.panel-fade-enter-from,
.panel-fade-leave-to {
  opacity: 0;
  max-height: 0;
  transform: translateY(-10px);
}
</style>
