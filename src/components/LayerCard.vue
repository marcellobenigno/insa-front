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
            v-if="legend"
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
          <div class="legend-container">
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
.layer-card {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 8px;
  transition: all 0.2s ease;
  overflow: hidden;
}

.layer-card:hover {
  background: rgba(255, 255, 255, 0.06);
  border-color: rgba(255, 255, 255, 0.15);
}

.layer-card.is-active {
  border-left: 3px solid var(--accent, #00d4aa);
  background: rgba(255, 255, 255, 0.05);
}

.layer-main-row {
  display: flex;
  align-items: center;
  padding: 10px;
  gap: 12px;
}

/* Visibility Toggle */
.visibility-toggle {
  width: 32px;
  height: 32px;
  border-radius: 6px;
  border: none;
  background: rgba(255, 255, 255, 0.05);
  color: #64748b;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.visibility-toggle:hover {
  background: rgba(255, 255, 255, 0.1);
  color: #f8fafc;
}

.visibility-toggle.is-visible {
  color: var(--accent, #00d4aa);
  background: rgba(0, 212, 170, 0.1);
}

/* Info */
.layer-info {
  flex: 1;
  min-width: 0;
}

.layer-label {
  display: block;
  font-size: 0.85rem;
  font-weight: 600;
  color: #f1f5f9;
  line-height: 1.2;
}

.layer-meta {
  display: block;
  font-size: 0.7rem;
  color: #94a3b8;
  margin-top: 2px;
}

/* Actions */
.layer-actions {
  display: flex;
  gap: 4px;
}

.action-btn {
  width: 28px;
  height: 28px;
  border-radius: 4px;
  border: none;
  background: transparent;
  color: #94a3b8;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.action-btn:hover {
  background: rgba(255, 255, 255, 0.08);
  color: #f8fafc;
}

.action-btn.is-panel-open {
  background: #3b82f6;
  color: white;
}

/* Sub Panels */
.layer-sub-panel {
  background: rgba(0, 0, 0, 0.2);
  border-top: 1px solid rgba(255, 255, 255, 0.05);
}

.panel-content {
  padding: 12px;
}

.panel-label {
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  color: #64748b;
  margin: 0;
}

.custom-slider {
  accent-color: var(--accent, #00d4aa);
}

.legend-container {
  background: rgba(255, 255, 255, 0.05);
  padding: 8px;
  border-radius: 4px;
}

/* Transitions */
.panel-fade-enter-active,
.panel-fade-leave-active {
  transition: all 0.25s ease;
  max-height: 200px;
}

.panel-fade-enter-from,
.panel-fade-leave-to {
  opacity: 0;
  max-height: 0;
  transform: translateY(-10px);
}
</style>
