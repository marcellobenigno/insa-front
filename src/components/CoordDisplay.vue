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
  bottom: 10px;
  left: 10px;
  z-index: 1000;
  padding: 6px 8px 6px 10px;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.82);
  backdrop-filter: saturate(180%) blur(20px);
  -webkit-backdrop-filter: saturate(180%) blur(20px);
  border: 1px solid rgba(0, 0, 0, 0.08);
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 6px;
  user-select: none;
  transition: opacity 0.2s;
}

[data-theme="dark"] .coord-display {
  background: rgba(28, 28, 30, 0.85);
  border-color: rgba(255, 255, 255, 0.12);
}

.coord-display--collapsed {
  padding: 6px 8px;
}

.coord-rows {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.coord-row {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 11px;
  font-family: 'JetBrains Mono', 'Fira Code', 'Courier New', monospace;
  color: #1d1d1f;
  white-space: nowrap;
  pointer-events: none;
}

[data-theme="dark"] .coord-row {
  color: #f5f5f7;
}

.coord-row--hint {
  font-family: -apple-system, BlinkMacSystemFont, sans-serif;
  color: #7a7a7a;
  font-size: 11px;
}

.coord-val {
  min-width: 88px;
}

.coord-sep {
  color: #c7c7cc;
  flex-shrink: 0;
}

[data-theme="dark"] .coord-sep {
  color: rgba(255, 255, 255, 0.2);
}

/* ── Botão de toggle ─────────────────────────────────────────────────────────── */
.coord-toggle {
  flex-shrink: 0;
  width: 20px;
  height: 20px;
  border: none;
  background: none;
  color: #7a7a7a;
  cursor: pointer;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  padding: 0;
  transition: color 0.15s, transform 0.1s;
}

.coord-toggle:hover {
  color: #1d1d1f;
}

[data-theme="dark"] .coord-toggle:hover {
  color: #f5f5f7;
}

.coord-toggle:active {
  transform: scale(0.9);
}

@media (max-width: 768px) {
  .coord-display { display: none; }
}
</style>
