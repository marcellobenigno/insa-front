<script setup>
import { ref, computed, watch } from 'vue'
import { useMapStore } from '@/stores/mapStore'
import stylesData from '@/assets/styles.json'
import statsData  from '@/assets/stats.json'
import LayerChartModal from './LayerChartModal.vue'

const props = defineProps({
  layerKey:     { type: String,  required: true },
  type:         { type: String,  required: true }, // 'base' | 'overlay'
  label:        { type: String,  required: true },
  meta:         { type: String,  default: '' },
  legend:       { type: String,  default: null },
  sourceLayer:  { type: String,  default: '' },
  searchFields: { type: Array,   default: () => [] },
  fieldTypes:   { type: Object,  default: () => ({}) },
  descFields:   { type: Object,  default: () => ({}) },
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

const activePanel   = ref(null)
const showChart     = ref(false)
const searchQuery   = ref('')
const searchOperator = ref('=')
const selectedField  = ref(props.searchFields[0] ?? '')

// Tipo do campo selecionado (number | string)
const isNumericField = computed(() =>
  props.fieldTypes?.[selectedField.value] === 'number'
)

// Filtro ativo no store para esta camada
const activeFilter = computed(() => store.layerSearchFilters?.[props.layerKey] ?? null)

// Gráfico disponível se a entrada existe e tem classes
const hasStats = computed(() => {
  const entry = statsData[props.sourceLayer]
  return entry != null && entry.classes?.length > 0
})

// Rótulo amigável de um campo — fallback para o próprio nome do campo
function fieldLabel(fieldName) {
  return props.descFields?.[fieldName] ?? fieldName
}

// Fecha painéis se a sidebar colapsar
watch(
  () => props.collapsed,
  (val) => { if (val) activePanel.value = null },
)

// Reseta operador ao trocar campo
watch(selectedField, () => { searchOperator.value = '=' })

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

// ── Busca ─────────────────────────────────────────────────────────────────────

function executeSearch() {
  const val = String(searchQuery.value ?? '').trim()
  if (!val) return
  store.setSearchFilter(props.layerKey, {
    field:    selectedField.value,
    operator: isNumericField.value ? searchOperator.value : '=',
    value:    val,
  })
}

function clearSearch() {
  searchQuery.value    = ''
  searchOperator.value = '='
  store.clearSearchFilter(props.layerKey)
}

// ── Legenda dinâmica via styles.json ──────────────────────────────────────────

const legendItems = computed(() => {
  const style = stylesData[props.layerKey]
  if (!style?.classes?.length) return []

  return style.classes.map(c => ({
    label: c.label,
    color: c.color,
    strokeOnly: style.type === 'stroke',
  }))
})

const hasLegend = computed(() => legendItems.value.length > 0 || !!props.legend)
</script>

<template>
  <div 
    class="layer-card" 
    :class="{ 'is-active': isVisible }"
  >
    <!-- Linha Principal -->
    <div class="layer-main-row" @click="toggleVisibility">
      <button
        class="visibility-toggle"
        :class="{ 'is-visible': isVisible }"
        :title="isVisible ? 'Ocultar camada' : 'Exibir camada'"
        :aria-label="isVisible ? `Ocultar ${label}` : `Exibir ${label}`"
        @click.stop="toggleVisibility"
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
          @click.stop="togglePanel('opacity')"
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
            @click.stop="togglePanel('legend')"
          >
            <i class="bi bi-palette" aria-hidden="true" />
          </button>
          
          <button
            v-if="searchFields.length > 0"
            class="action-btn"
            :class="{ 'is-panel-open': activePanel === 'search' }"
            title="Buscar na camada"
            aria-label="Buscar na camada"
            @click.stop="togglePanel('search')"
          >
            <i class="bi bi-search" aria-hidden="true" />
          </button>

          <button
            v-if="hasStats"
            class="action-btn"
            :title="'Ver gráfico — ' + label"
            aria-label="Ver gráfico de área"
            @click.stop="showChart = true"
          >
            <i class="bi bi-bar-chart-fill" aria-hidden="true" />
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
            <span class="badge opacity-value-badge">{{ Math.round(opacity * 100) }}%</span>
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
              <span
                class="legend-swatch"
                :style="item.strokeOnly
                  ? { background: 'transparent', border: `3px solid ${item.color}` }
                  : { background: item.color, border: '1px solid rgba(255,255,255,0.15)' }"
              />
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
          <div class="d-flex justify-content-between align-items-center mb-2">
            <label class="panel-label">Buscar por {{ fieldLabel(selectedField) }}</label>
            <button
              v-if="activeFilter"
              class="btn-clear-search"
              title="Limpar filtro"
              @click="clearSearch"
            >
              <i class="bi bi-x-circle-fill" /> Limpar
            </button>
          </div>

          <!-- Indicador de filtro ativo -->
          <div v-if="activeFilter" class="filter-badge mb-2">
            <i class="bi bi-funnel-fill" />
            {{ fieldLabel(activeFilter.field) }}
            <template v-if="isNumericField"> {{ activeFilter.operator }}</template>
            <template v-else> contém</template>
            <strong>{{ activeFilter.value }}</strong>
          </div>

          <!-- Feedback: zero resultados -->
          <div v-if="activeFilter && store.layerSearchMatchCounts?.[layerKey] === 0" class="no-results-badge mb-2">
            <i class="bi bi-exclamation-circle-fill" />
            Nenhum resultado encontrado
          </div>

          <div class="search-form">
            <!-- Campo -->
            <select
              v-if="searchFields.length > 1"
              v-model="selectedField"
              class="form-select form-select-sm mb-2 search-field"
            >
              <option v-for="f in searchFields" :key="f" :value="f">{{ fieldLabel(f) }}</option>
            </select>

            <!-- Operador (só numérico) + Valor -->
            <div class="search-input-row">
              <select
                v-if="isNumericField"
                v-model="searchOperator"
                class="form-select form-select-sm operator-select search-field"
              >
                <option value="=">=</option>
                <option value=">">&gt;</option>
                <option value=">=">&gt;=</option>
                <option value="<">&lt;</option>
                <option value="<=">&lt;=</option>
              </select>
              <input
                v-model="searchQuery"
                :type="isNumericField ? 'number' : 'text'"
                class="form-control form-control-sm search-field"
                :placeholder="isNumericField ? 'Valor numérico… ↵' : `Buscar em ${fieldLabel(selectedField)}… ↵`"
                title="Pressione Enter para buscar"
                @keyup.enter="executeSearch"
              />
            </div>
          </div>
        </div>

      </div>
    </Transition>
  </div>

  <LayerChartModal
    v-if="showChart"
    :source-layer="sourceLayer"
    :label="label"
    @close="showChart = false"
  />
</template>

<style scoped>
/* ── Card ────────────────────────────────────────────────────────────────────── */
.layer-card {
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid var(--border-color);
  background: var(--card-bg);
  transition: background 0.15s, border-color 0.15s;
}

.layer-card:hover {
  background: var(--card-bg-hover);
}

.layer-card.is-active {
  border: 1px solid var(--accent);
  background: var(--card-bg-active);
}

.layer-main-row {
  display: flex;
  align-items: center;
  padding: 8px 8px 8px 10px;
  gap: 8px;
  cursor: pointer;
}

/* ── Botão de visibilidade ───────────────────────────────────────────────────── */
.visibility-toggle {
  width: 26px;
  height: 26px;
  border: none;
  border-radius: 6px;
  background: var(--btn-bg);
  color: var(--text-dim);
  cursor: pointer;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  transition: background 0.15s, color 0.15s;
}

.visibility-toggle:hover {
  background: var(--btn-bg-hover);
  color: var(--text-main);
}

.visibility-toggle:active {
  transform: scale(0.95);
}

.visibility-toggle.is-visible {
  background: var(--bg-accent-dim);
  color: var(--accent);
}

/* ── Info da camada ──────────────────────────────────────────────────────────── */
.layer-info {
  flex: 1;
  min-width: 0;
}

.layer-label {
  display: block;
  font-size: 13px;
  font-weight: 600;
  letter-spacing: -0.224px;
  line-height: 1.3;
  color: var(--text-main);
}

.layer-meta {
  display: block;
  font-size: 11px;
  margin-top: 1px;
  color: var(--text-muted);
}

/* ── Ações ───────────────────────────────────────────────────────────────────── */
.layer-actions {
  display: flex;
  gap: 3px;
}

.action-btn {
  width: 24px;
  height: 24px;
  border: none;
  border-radius: 6px;
  background: transparent;
  color: var(--text-muted);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  transition: background 0.15s, color 0.15s;
}

.action-btn:hover {
  background: var(--hover-overlay);
  color: var(--text-main);
}

.action-btn:active {
  transform: scale(0.92);
}

.action-btn.is-panel-open {
  background: var(--accent);
  color: #ffffff;
}

/* ── Painéis expansíveis ─────────────────────────────────────────────────────── */
.layer-sub-panel {
  border-top: 1px solid var(--border-color);
  background: var(--card-bg-hover);
}

.panel-content {
  padding: 11px 12px;
}

.panel-label {
  margin: 0;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--text-muted);
}

.custom-slider {
  accent-color: var(--accent);
  cursor: pointer;
}

.custom-slider::-webkit-slider-runnable-track {
  height: 3px;
  border-radius: 2px;
  background: var(--border-color);
}

.custom-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 14px;
  height: 14px;
  border-radius: 50%;
  background: var(--accent);
  margin-top: -5.5px;
  box-shadow: none;
  cursor: pointer;
}

.custom-slider::-moz-range-track {
  height: 3px;
  border-radius: 2px;
  background: var(--border-color);
}

.custom-slider::-moz-range-thumb {
  width: 14px;
  height: 14px;
  border-radius: 50%;
  background: var(--accent);
  border: none;
  cursor: pointer;
}

/* ── Legenda dinâmica ────────────────────────────────────────────────────────── */
.legend-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
  max-height: 200px;
  overflow-y: auto;
  padding-right: 4px;
  scrollbar-width: thin;
  scrollbar-color: var(--border-color) transparent;
}

.legend-list::-webkit-scrollbar       { width: 4px; }
.legend-list::-webkit-scrollbar-track  { background: transparent; }
.legend-list::-webkit-scrollbar-thumb  { background: var(--border-color); border-radius: 2px; }

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.legend-swatch {
  flex-shrink: 0;
  width: 20px;
  height: 12px;
  border-radius: 4px;
}

.legend-item-label {
  font-size: 12px;
  font-weight: 400;
  letter-spacing: -0.12px;
  line-height: 1.4;
  word-break: break-word;
  color: var(--text-main);
}

/* ── Legenda estática (imagem) ───────────────────────────────────────────────── */
.legend-container {
  padding: 8px;
  border-radius: 8px;
  background: var(--btn-bg);
}

/* ── Busca ───────────────────────────────────────────────────────────────────── */
.search-input-row {
  display: flex;
  gap: 6px;
  align-items: center;
}

.search-input-row .form-control {
  flex: 1;
  min-width: 0;
}

.operator-select {
  flex: 0 0 58px;
  min-width: 58px;
  padding: 0 4px;
  text-align: center;
  background-image: none;
}

.search-field {
  background-color: var(--bg-sidebar) !important;
  color: var(--text-main) !important;
  border-color: var(--border-color) !important;
  border-radius: 8px !important;
  font-size: 13px !important;
}

.search-field:focus {
  background-color: var(--bg-sidebar) !important;
  color: var(--text-main) !important;
  border-color: var(--accent) !important;
  box-shadow: 0 0 0 3px var(--bg-accent-dim) !important;
}

.filter-badge {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 4px 8px;
  border-radius: 8px;
  background: var(--bg-accent-dim);
  border: 1px solid rgba(0, 102, 204, 0.2);
  font-size: 12px;
  color: var(--accent);
}

[data-theme="dark"] .filter-badge {
  border-color: rgba(41, 151, 255, 0.25);
}

.filter-badge strong {
  color: var(--accent);
}

.no-results-badge {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 4px 8px;
  border-radius: 8px;
  background: rgba(255, 59, 48, 0.06);
  border: 1px solid rgba(255, 59, 48, 0.2);
  font-size: 12px;
  color: rgb(255, 59, 48);
}

.opacity-value-badge {
  background: var(--btn-bg);
  color: var(--text-main);
  border-radius: 6px;
  padding: 1px 8px;
  font-size: 12px;
  font-weight: 600;
}

.btn-clear-search {
  display: flex;
  align-items: center;
  gap: 4px;
  border: none;
  background: none;
  font-size: 12px;
  color: var(--text-dim);
  cursor: pointer;
  padding: 2px 6px;
  border-radius: 6px;
  transition: color 0.15s, background 0.15s;
}

.btn-clear-search:hover {
  color: rgb(255, 59, 48);
  background: rgba(255, 59, 48, 0.06);
}

/* ── Transição de painel ─────────────────────────────────────────────────────── */
.panel-fade-enter-active,
.panel-fade-leave-active {
  max-height: 300px;
  transition: opacity 0.2s ease, max-height 0.2s ease, transform 0.2s ease;
}

.panel-fade-enter-from,
.panel-fade-leave-to {
  opacity: 0;
  max-height: 0;
  transform: translateY(-8px);
}
</style>
