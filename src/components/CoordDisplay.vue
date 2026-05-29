<script setup>
import { computed, ref } from 'vue'
import { useMapStore } from '@/stores/mapStore'

const store = useMapStore()
const isVisible = ref(true)

// ── Conversão DD → DMS ────────────────────────────────────────────────────────
function ddToDms(dd) {
  const abs     = Math.abs(dd)
  const deg     = Math.floor(abs)
  const minFrac = (abs - deg) * 60
  const min     = Math.floor(minFrac)
  const sec     = Math.round((minFrac - min) * 60)
  return { deg, min, sec }
}

function pad(n) { return String(n).padStart(2, '0') }

// ── Computed ──────────────────────────────────────────────────────────────────
const dd = computed(() => {
  const c = store.mouseCoords
  if (!c) return null
  return {
    lat: c.lat.toFixed(5),
    lng: c.lng.toFixed(5),
  }
})

const dms = computed(() => {
  const c = store.mouseCoords
  if (!c) return null
  const lat = ddToDms(c.lat)
  const lng = ddToDms(c.lng)
  return {
    lat: `${lat.deg}° ${pad(lat.min)}' ${pad(lat.sec)}'' ${c.lat >= 0 ? 'N' : 'S'}`,
    lng: `${lng.deg}° ${pad(lng.min)}' ${pad(lng.sec)}'' ${c.lng >= 0 ? 'E' : 'W'}`,
  }
})
</script>

<template>
  <div
    class="coord-display"
    :class="{ 'coord-display--ready': !!dd, 'coord-display--collapsed': !isVisible }"
    aria-live="off"
    aria-label="Coordenadas do cursor"
  >
    <div v-if="isVisible" class="coord-rows">
      <template v-if="dd">
        <div class="coord-row">
          <span class="coord-val">{{ dd.lat }}</span>
          <span class="coord-sep" aria-hidden="true">|</span>
          <span class="coord-val">{{ dd.lng }}</span>
        </div>
        <div class="coord-row">
          <span class="coord-val">{{ dms.lat }}</span>
          <span class="coord-sep" aria-hidden="true">|</span>
          <span class="coord-val">{{ dms.lng }}</span>
        </div>
      </template>
      <template v-else>
        <div class="coord-row coord-row--hint">
          <i class="bi bi-cursor" aria-hidden="true" />
          <span>Mova o cursor sobre o mapa</span>
        </div>
      </template>
    </div>

    <button
      class="coord-toggle"
      :title="isVisible ? 'Ocultar coordenadas' : 'Exibir coordenadas'"
      :aria-label="isVisible ? 'Ocultar coordenadas' : 'Exibir coordenadas'"
      @click="isVisible = !isVisible"
    >
      <i class="bi" :class="isVisible ? 'bi-eye-slash' : 'bi-crosshair'" aria-hidden="true" />
    </button>
  </div>
</template>

<style scoped>
.coord-display {
  position: absolute;
  bottom: 8px;
  left: 10px;
  z-index: 1000;
  padding: 5px 6px 5px 9px;
  border-radius: 8px;
  background: var(--bg-sidebar);
  border: 1px solid var(--border-color);
  backdrop-filter: blur(6px);
  -webkit-backdrop-filter: blur(6px);
  box-shadow: var(--shadow-lg);
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 6px;
  user-select: none;
  transition: opacity 0.2s, background 0.3s, border-color 0.3s;
}

.coord-display--collapsed {
  padding: 5px 6px;
}

/* Coluna de linhas de coordenadas */
.coord-rows {
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.coord-row {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.66rem;
  font-family: 'JetBrains Mono', 'Fira Code', 'Courier New', monospace;
  color: var(--text-main);
  white-space: nowrap;
  pointer-events: none;
}

.coord-row--hint {
  font-family: 'Inter', sans-serif;
  color: var(--text-dim);
  font-size: 0.66rem;
}

.coord-val {
  color: var(--text-main);
  min-width: 90px;
}

.coord-sep {
  color: var(--text-dim);
  flex-shrink: 0;
}

/* ── Botão de toggle ─────────────────────────────────────────────────────────── */
.coord-toggle {
  flex-shrink: 0;
  width: 22px;
  height: 22px;
  border: none;
  background: none;
  color: var(--text-dim);
  cursor: pointer;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  padding: 0;
  transition: color 0.15s, background 0.15s;
}

.coord-toggle:hover {
  color: var(--accent);
  background: var(--hover-overlay);
}

@media (max-width: 768px) {
  .coord-display {
    display: none;
  }
}
</style>
