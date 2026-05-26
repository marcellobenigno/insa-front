<script setup>
import { ref, computed, onUnmounted, nextTick } from 'vue'
import { useMapStore } from '@/stores/mapStore'
import { useSidebar } from '@/composables/useSidebar'

const store  = useMapStore()
const { isCollapsed, toggleSidebar } = useSidebar()

// ── Modos disponíveis ──────────────────────────────────────────────────────────
const MODES = [
  { key: 'address', label: 'Endereço ou local',       icon: 'bi-geo-alt'   },
  { key: 'dd',      label: 'Lat/Long Graus Decimais', icon: 'bi-crosshair' },
  { key: 'dms',     label: 'Lat/Long G°M′S″ (DMS)',   icon: 'bi-compass'   },
]

const mode        = ref('address')
const showMenu    = ref(false)
const rootEl      = ref(null)
const currentMode = computed(() => MODES.find(m => m.key === mode.value))

// ── Estado compartilhado ───────────────────────────────────────────────────────
const loading = ref(false)
const error   = ref('')

// ── Modo: Endereço ─────────────────────────────────────────────────────────────
const query       = ref('')
const suggestions = ref([])

// ── Modo: DD ───────────────────────────────────────────────────────────────────
const ddLat = ref('')
const ddLng = ref('')

// ── Modo: DMS ──────────────────────────────────────────────────────────────────
const dmsLatDeg = ref(''); const dmsLatMin = ref(''); const dmsLatSec = ref(''); const dmsLatDir = ref('S')
const dmsLngDeg = ref(''); const dmsLngMin = ref(''); const dmsLngSec = ref(''); const dmsLngDir = ref('W')

// ── Limites da área de interesse (espelha paraibaBounds em MapContainer) ───────
const LAT_MIN = -8.3,   LAT_MAX = -6.02
const LNG_MIN = -38.76, LNG_MAX = -35.17

// ── Nominatim com debounce e cancelamento ──────────────────────────────────────
let debounceTimer = null
let abortCtrl     = null

function onQueryInput() {
  clearTimeout(debounceTimer)
  suggestions.value = []
  error.value       = ''
  if (query.value.trim().length < 3) return
  debounceTimer = setTimeout(() => fetchNominatim(query.value.trim()), 400)
}

async function fetchNominatim(q) {
  if (abortCtrl) abortCtrl.abort()
  abortCtrl     = new AbortController()
  loading.value = true
  try {
    const params = new URLSearchParams({
      format: 'json',
      q,
      limit: '5',
      viewbox: `${LNG_MIN},${LAT_MAX},${LNG_MAX},${LAT_MIN}`,
      bounded: '0',
    })
    const res  = await fetch(`https://nominatim.openstreetmap.org/search?${params}`, {
      signal:  abortCtrl.signal,
      headers: { 'Accept-Language': 'pt-BR,pt;q=0.9' },
    })
    const data = await res.json()
    suggestions.value = data
    if (!data.length) error.value = 'Nenhum resultado encontrado.'
  } catch (e) {
    if (e.name !== 'AbortError') error.value = 'Erro na busca. Verifique sua conexão.'
  } finally {
    loading.value = false
  }
}

function selectSuggestion(s) {
  const lat   = parseFloat(s.lat)
  const lng   = parseFloat(s.lon)
  const label = shortLabel(s.display_name)
  store.setGeoLocation({ lat, lng, label })
  query.value       = label
  suggestions.value = []
  error.value       = ''
}

// Retorna as duas primeiras partes da display_name (antes da segunda vírgula)
function shortLabel(displayName) {
  const parts = displayName.split(',')
  return parts.slice(0, 2).join(',').trim()
}

function clearQuery() {
  query.value       = ''
  suggestions.value = []
  error.value       = ''
  store.clearGeoLocation()
}

// ── Modo DD ────────────────────────────────────────────────────────────────────
function submitDD() {
  const lat = parseFloat(ddLat.value)
  const lng = parseFloat(ddLng.value)
  if (isNaN(lat) || isNaN(lng)) {
    error.value = 'Informe latitude e longitude válidas.'
    return
  }
  if (!inBounds(lat, lng)) {
    error.value = `Fora da área. Lat ${LAT_MIN}…${LAT_MAX} | Lng ${LNG_MIN}…${LNG_MAX}`
    return
  }
  error.value = ''
  store.setGeoLocation({ lat, lng, label: `${lat.toFixed(5)}, ${lng.toFixed(5)}` })
}

// ── Modo DMS ───────────────────────────────────────────────────────────────────
function dmsToDD(deg, min, sec, dir) {
  const dd = Math.abs(Number(deg)) + Number(min) / 60 + Number(sec) / 3600
  return (dir === 'S' || dir === 'W') ? -dd : dd
}

function submitDMS() {
  const fields = [dmsLatDeg, dmsLatMin, dmsLatSec, dmsLngDeg, dmsLngMin, dmsLngSec]
  if (fields.some(f => f.value === '')) {
    error.value = 'Preencha todos os campos.'
    return
  }
  const lat = dmsToDD(dmsLatDeg.value, dmsLatMin.value, dmsLatSec.value, dmsLatDir.value)
  const lng = dmsToDD(dmsLngDeg.value, dmsLngMin.value, dmsLngSec.value, dmsLngDir.value)
  if (isNaN(lat) || isNaN(lng)) { error.value = 'Valores inválidos.'; return }
  if (!inBounds(lat, lng)) {
    error.value = `Fora da área. Lat ${LAT_MIN}…${LAT_MAX} | Lng ${LNG_MIN}…${LNG_MAX}`
    return
  }
  const fmt = (d, m, s, dir) => `${d}°${m}′${Number(s).toFixed(1)}″${dir}`
  error.value = ''
  store.setGeoLocation({
    lat, lng,
    label: `${fmt(dmsLatDeg.value, dmsLatMin.value, dmsLatSec.value, dmsLatDir.value)} `
         + `${fmt(dmsLngDeg.value, dmsLngMin.value, dmsLngSec.value, dmsLngDir.value)}`,
  })
}

// ── Helpers ────────────────────────────────────────────────────────────────────
function inBounds(lat, lng) {
  return lat >= LAT_MIN && lat <= LAT_MAX && lng >= LNG_MIN && lng <= LNG_MAX
}

function selectMode(key) {
  mode.value     = key
  showMenu.value = false
  resetAll()
}

function resetAll() {
  clearTimeout(debounceTimer)
  if (abortCtrl) { abortCtrl.abort(); abortCtrl = null }
  query.value = ''; suggestions.value = []; loading.value = false; error.value = ''
  ddLat.value = ''; ddLng.value = ''
  dmsLatDeg.value = ''; dmsLatMin.value = ''; dmsLatSec.value = ''; dmsLatDir.value = 'S'
  dmsLngDeg.value = ''; dmsLngMin.value = ''; dmsLngSec.value = ''; dmsLngDir.value = 'W'
  store.clearGeoLocation()
}

// ── Menu dropdown — fechar ao clicar fora ─────────────────────────────────────
function openMenu() {
  showMenu.value = !showMenu.value
  if (showMenu.value) {
    nextTick(() => document.addEventListener('click', onDocClick))
  } else {
    document.removeEventListener('click', onDocClick)
  }
}

function onDocClick(e) {
  if (!rootEl.value?.contains(e.target)) {
    showMenu.value = false
    document.removeEventListener('click', onDocClick)
  }
}

// ── Sidebar colapsada ─────────────────────────────────────────────────────────
function handleCollapsedClick() {
  toggleSidebar()
}

onUnmounted(() => {
  clearTimeout(debounceTimer)
  if (abortCtrl) abortCtrl.abort()
  document.removeEventListener('click', onDocClick)
})
</script>

<template>
  <footer ref="rootEl" class="gs-footer" :class="{ 'gs-footer--collapsed': isCollapsed }">

    <!-- ── Sidebar colapsada: ícone clicável ─────────────────────────────────── -->
    <button
      v-if="isCollapsed"
      class="gs-icon-btn"
      title="Abrir busca geoespacial"
      aria-label="Abrir busca geoespacial"
      @click="handleCollapsedClick"
    >
      <i class="bi bi-search" aria-hidden="true" />
    </button>

    <!-- ── Sidebar expandida: painel completo ────────────────────────────────── -->
    <div v-else class="gs-panel">

      <!-- Cabeçalho: rótulo + seletor de modo -->
      <div class="gs-header">
        <span class="gs-title">Busca</span>

        <div class="gs-mode-wrap" :class="{ 'gs-mode-wrap--open': showMenu }">
          <button
            class="gs-mode-btn"
            :title="currentMode.label"
            :aria-label="`Modo atual: ${currentMode.label}. Clique para mudar.`"
            :aria-expanded="showMenu"
            aria-haspopup="listbox"
            @click.stop="openMenu"
          >
            <i class="bi" :class="currentMode.icon" aria-hidden="true" />
            <span class="gs-mode-label">{{ currentMode.label }}</span>
            <i class="bi bi-chevron-down gs-caret" :class="{ 'gs-caret--open': showMenu }" aria-hidden="true" />
          </button>

          <!-- Dropdown de modos -->
          <ul v-if="showMenu" class="gs-menu" role="listbox" aria-label="Modos de busca">
            <li
              v-for="m in MODES"
              :key="m.key"
              class="gs-menu-item"
              :class="{ 'gs-menu-item--active': m.key === mode }"
              role="option"
              :aria-selected="m.key === mode"
              @click="selectMode(m.key)"
            >
              <i class="bi" :class="m.icon" aria-hidden="true" />
              {{ m.label }}
            </li>
          </ul>
        </div>
      </div>

      <!-- ── Modo: Endereço ──────────────────────────────────────────────────── -->
      <div v-if="mode === 'address'" class="gs-body">
        <div class="gs-input-wrap" :class="{ 'gs-input-wrap--loading': loading }">
          <i class="bi bi-search gs-input-icon" aria-hidden="true" />
          <input
            v-model="query"
            type="search"
            class="gs-input"
            placeholder="Endereço ou local… ↵"
            autocomplete="off"
            aria-label="Buscar endereço ou local"
            aria-autocomplete="list"
            aria-controls="gs-suggestions"
            @input="onQueryInput"
            @keydown.esc="suggestions = []"
          />
          <button
            v-if="query"
            class="gs-clear-btn"
            title="Limpar"
            aria-label="Limpar busca"
            @click="clearQuery"
          >
            <i class="bi bi-x" aria-hidden="true" />
          </button>
          <span v-if="loading" class="gs-spinner" aria-label="Buscando…" role="status">
            <i class="bi bi-arrow-clockwise" aria-hidden="true" />
          </span>
        </div>

        <!-- Sugestões -->
        <ul
          v-if="suggestions.length"
          id="gs-suggestions"
          class="gs-suggestions"
          role="listbox"
          aria-label="Sugestões"
        >
          <li
            v-for="s in suggestions"
            :key="s.place_id"
            class="gs-suggestion"
            role="option"
            :title="s.display_name"
            @mousedown.prevent="selectSuggestion(s)"
          >
            <i class="bi bi-pin-map" aria-hidden="true" />
            <span class="gs-suggestion-text">{{ s.display_name }}</span>
          </li>
        </ul>
      </div>

      <!-- ── Modo: DD (Graus Decimais) ──────────────────────────────────────── -->
      <div v-if="mode === 'dd'" class="gs-body">
        <div class="gs-coords">
          <div class="gs-coord-row">
            <label class="gs-coord-label" for="gs-dd-lat">Latitude</label>
            <input
              id="gs-dd-lat"
              v-model="ddLat"
              type="number"
              step="0.00001"
              class="gs-coord-input"
              placeholder="-7.12345"
              aria-label="Latitude em graus decimais"
              @keyup.enter="submitDD"
            />
          </div>
          <div class="gs-coord-row">
            <label class="gs-coord-label" for="gs-dd-lng">Longitude</label>
            <input
              id="gs-dd-lng"
              v-model="ddLng"
              type="number"
              step="0.00001"
              class="gs-coord-input"
              placeholder="-37.12345"
              aria-label="Longitude em graus decimais"
              @keyup.enter="submitDD"
            />
          </div>
        </div>
        <button class="gs-submit-btn" @click="submitDD">
          <i class="bi bi-arrow-right-circle" aria-hidden="true" /> Ir
        </button>
      </div>

      <!-- ── Modo: DMS (Graus, Minutos, Segundos) ────────────────────────────── -->
      <div v-if="mode === 'dms'" class="gs-body">
        <div class="gs-coords">

          <!-- Latitude DMS -->
          <fieldset class="gs-dms-fieldset">
            <legend class="gs-coord-label">Latitude</legend>
            <div class="gs-dms-row">
              <input
                v-model="dmsLatDeg"
                type="number" min="0" max="90" step="1"
                class="gs-dms-input"
                placeholder="°"
                aria-label="Graus de latitude"
                @keyup.enter="submitDMS"
              /><span class="gs-dms-sep">°</span>
              <input
                v-model="dmsLatMin"
                type="number" min="0" max="59" step="1"
                class="gs-dms-input"
                placeholder="′"
                aria-label="Minutos de latitude"
                @keyup.enter="submitDMS"
              /><span class="gs-dms-sep">′</span>
              <input
                v-model="dmsLatSec"
                type="number" min="0" max="59.999" step="0.001"
                class="gs-dms-input"
                placeholder="″"
                aria-label="Segundos de latitude"
                @keyup.enter="submitDMS"
              /><span class="gs-dms-sep">″</span>
              <select
                v-model="dmsLatDir"
                class="gs-dms-dir"
                aria-label="Direção de latitude"
              >
                <option value="S">S</option>
                <option value="N">N</option>
              </select>
            </div>
          </fieldset>

          <!-- Longitude DMS -->
          <fieldset class="gs-dms-fieldset">
            <legend class="gs-coord-label">Longitude</legend>
            <div class="gs-dms-row">
              <input
                v-model="dmsLngDeg"
                type="number" min="0" max="180" step="1"
                class="gs-dms-input"
                placeholder="°"
                aria-label="Graus de longitude"
                @keyup.enter="submitDMS"
              /><span class="gs-dms-sep">°</span>
              <input
                v-model="dmsLngMin"
                type="number" min="0" max="59" step="1"
                class="gs-dms-input"
                placeholder="′"
                aria-label="Minutos de longitude"
                @keyup.enter="submitDMS"
              /><span class="gs-dms-sep">′</span>
              <input
                v-model="dmsLngSec"
                type="number" min="0" max="59.999" step="0.001"
                class="gs-dms-input"
                placeholder="″"
                aria-label="Segundos de longitude"
                @keyup.enter="submitDMS"
              /><span class="gs-dms-sep">″</span>
              <select
                v-model="dmsLngDir"
                class="gs-dms-dir"
                aria-label="Direção de longitude"
              >
                <option value="W">W</option>
                <option value="E">E</option>
              </select>
            </div>
          </fieldset>
        </div>
        <button class="gs-submit-btn" @click="submitDMS">
          <i class="bi bi-arrow-right-circle" aria-hidden="true" /> Ir
        </button>
      </div>

      <!-- ── Mensagem de erro ────────────────────────────────────────────────── -->
      <div v-if="error" class="gs-error" role="alert">
        <i class="bi bi-exclamation-triangle-fill" aria-hidden="true" />
        {{ error }}
      </div>

      <!-- ── Pin ativo ──────────────────────────────────────────────────────── -->
      <div v-if="store.geoLocation" class="gs-active-pin">
        <i class="bi bi-pin-map-fill" aria-hidden="true" />
        <span class="gs-active-label" :title="store.geoLocation.label">{{ store.geoLocation.label }}</span>
        <button
          class="gs-active-clear"
          title="Remover marcador"
          aria-label="Remover marcador do mapa"
          @click="store.clearGeoLocation()"
        >
          <i class="bi bi-x" aria-hidden="true" />
        </button>
      </div>

    </div>
  </footer>
</template>

<style scoped>
/* ── Footer wrapper ──────────────────────────────────────────────────────────── */
.gs-footer {
  flex-shrink: 0;
  border-top: 1px solid var(--border-color);
  background: rgba(0, 0, 0, 0.25);
}

.gs-footer--collapsed {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 14px 0;
}

/* ── Ícone colapsado ─────────────────────────────────────────────────────────── */
.gs-icon-btn {
  width: 36px;
  height: 36px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.04);
  color: var(--text-muted);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
  transition: background 0.2s, color 0.2s, border-color 0.2s;
}

.gs-icon-btn:hover {
  background: var(--bg-accent-dim);
  color: var(--accent);
  border-color: var(--accent);
}

/* ── Painel expandido ────────────────────────────────────────────────────────── */
.gs-panel {
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

/* ── Cabeçalho ───────────────────────────────────────────────────────────────── */
.gs-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.gs-title {
  font-size: 0.7rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--text-dim);
  white-space: nowrap;
}

/* ── Seletor de modo ─────────────────────────────────────────────────────────── */
.gs-mode-wrap {
  position: relative;
  flex: 1;
  min-width: 0;
}

.gs-mode-btn {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 5px 8px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.04);
  color: var(--text-muted);
  font-size: 0.75rem;
  cursor: pointer;
  transition: background 0.2s, color 0.2s, border-color 0.2s;
  overflow: hidden;
}

.gs-mode-btn:hover,
.gs-mode-wrap--open .gs-mode-btn {
  background: rgba(255, 255, 255, 0.08);
  color: var(--text-main);
  border-color: rgba(255, 255, 255, 0.2);
}

.gs-mode-label {
  flex: 1;
  text-align: left;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.gs-caret {
  font-size: 0.65rem;
  flex-shrink: 0;
  transition: transform 0.2s;
}

.gs-caret--open {
  transform: rotate(-180deg);
}

/* ── Menu dropdown ───────────────────────────────────────────────────────────── */
.gs-menu {
  position: absolute;
  bottom: calc(100% + 6px);
  left: 0;
  right: 0;
  list-style: none;
  margin: 0;
  padding: 4px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: var(--bg-card);
  box-shadow: var(--shadow-lg);
  z-index: 200;
}

.gs-menu-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 10px;
  border-radius: 5px;
  font-size: 0.78rem;
  color: var(--text-muted);
  cursor: pointer;
  transition: background 0.15s, color 0.15s;
}

.gs-menu-item:hover {
  background: rgba(255, 255, 255, 0.07);
  color: var(--text-main);
}

.gs-menu-item--active {
  color: var(--accent);
  background: var(--bg-accent-dim);
}

/* ── Corpo do modo ───────────────────────────────────────────────────────────── */
.gs-body {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

/* ── Input de endereço ───────────────────────────────────────────────────────── */
.gs-input-wrap {
  position: relative;
  display: flex;
  align-items: center;
}

.gs-input-icon {
  position: absolute;
  left: 9px;
  color: var(--text-dim);
  font-size: 0.8rem;
  pointer-events: none;
}

.gs-input {
  width: 100%;
  padding: 7px 32px 7px 28px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  color: var(--text-main);
  font-size: 0.8rem;
  outline: none;
  transition: border-color 0.2s, background 0.2s;
}

.gs-input::placeholder { color: var(--text-dim); }

.gs-input:focus {
  border-color: var(--accent);
  background: rgba(255, 255, 255, 0.07);
}

/* Remove os ícones nativos do input type="search" */
.gs-input::-webkit-search-cancel-button,
.gs-input::-webkit-search-decoration { display: none; }

.gs-clear-btn {
  position: absolute;
  right: 6px;
  width: 20px;
  height: 20px;
  border: none;
  background: none;
  color: var(--text-dim);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 3px;
  transition: color 0.15s;
}

.gs-clear-btn:hover { color: var(--text-main); }

.gs-spinner {
  position: absolute;
  right: 8px;
  color: var(--accent);
  font-size: 0.85rem;
  animation: spin 0.8s linear infinite;
}

@keyframes spin { to { transform: rotate(360deg); } }

/* ── Lista de sugestões ──────────────────────────────────────────────────────── */
.gs-suggestions {
  list-style: none;
  margin: 0;
  padding: 4px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: var(--bg-card);
  box-shadow: var(--shadow-lg);
  max-height: 200px;
  overflow-y: auto;
  scrollbar-width: thin;
  scrollbar-color: var(--border-color) transparent;
}

.gs-suggestion {
  display: flex;
  align-items: flex-start;
  gap: 7px;
  padding: 7px 8px;
  border-radius: 5px;
  cursor: pointer;
  font-size: 0.76rem;
  color: var(--text-muted);
  transition: background 0.15s, color 0.15s;
}

.gs-suggestion:hover {
  background: rgba(255, 255, 255, 0.07);
  color: var(--text-main);
}

.gs-suggestion .bi { flex-shrink: 0; margin-top: 1px; }

.gs-suggestion-text {
  line-height: 1.4;
  word-break: break-word;
}

/* ── Coordenadas (DD e DMS) ──────────────────────────────────────────────────── */
.gs-coords {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.gs-coord-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.gs-coord-label {
  font-size: 0.7rem;
  font-weight: 600;
  color: var(--text-dim);
  white-space: nowrap;
  min-width: 56px;
  text-align: right;
}

.gs-coord-input {
  flex: 1;
  padding: 6px 8px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  color: var(--text-main);
  font-size: 0.8rem;
  outline: none;
  transition: border-color 0.2s;
}

.gs-coord-input::placeholder { color: var(--text-dim); }
.gs-coord-input:focus { border-color: var(--accent); }

/* Remove setas do input number */
.gs-coord-input::-webkit-inner-spin-button,
.gs-coord-input::-webkit-outer-spin-button { appearance: none; }

/* ── DMS ─────────────────────────────────────────────────────────────────────── */
.gs-dms-fieldset {
  border: none;
  padding: 0;
  margin: 0;
}

.gs-dms-row {
  display: flex;
  align-items: center;
  gap: 2px;
  margin-top: 4px;
}

.gs-dms-input {
  flex: 1;
  min-width: 0;
  padding: 6px 4px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--border-color);
  border-radius: 5px;
  color: var(--text-main);
  font-size: 0.78rem;
  text-align: center;
  outline: none;
  transition: border-color 0.2s;
}

.gs-dms-input::placeholder { color: var(--text-dim); }
.gs-dms-input:focus { border-color: var(--accent); }
.gs-dms-input::-webkit-inner-spin-button,
.gs-dms-input::-webkit-outer-spin-button { appearance: none; }

.gs-dms-sep {
  font-size: 0.75rem;
  color: var(--text-dim);
  padding: 0 1px;
  flex-shrink: 0;
}

.gs-dms-dir {
  padding: 6px 4px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--border-color);
  border-radius: 5px;
  color: var(--text-main);
  font-size: 0.78rem;
  cursor: pointer;
  outline: none;
  flex-shrink: 0;
}

.gs-dms-dir:focus { border-color: var(--accent); }

/* ── Botão submeter ──────────────────────────────────────────────────────────── */
.gs-submit-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  width: 100%;
  padding: 7px;
  border: none;
  border-radius: 6px;
  background: var(--accent);
  color: var(--text-on-accent);
  font-size: 0.8rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}

.gs-submit-btn:hover { background: var(--accent-hover); }

/* ── Erro ────────────────────────────────────────────────────────────────────── */
.gs-error {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 7px 9px;
  border-radius: 6px;
  background: rgba(248, 113, 113, 0.1);
  border: 1px solid rgba(248, 113, 113, 0.3);
  color: #f87171;
  font-size: 0.75rem;
  line-height: 1.4;
}

/* ── Pin ativo ───────────────────────────────────────────────────────────────── */
.gs-active-pin {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 8px;
  border-radius: 6px;
  background: var(--bg-accent-dim);
  border: 1px solid rgba(0, 212, 170, 0.25);
  color: var(--accent);
  font-size: 0.75rem;
}

.gs-active-label {
  flex: 1;
  min-width: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  color: var(--text-muted);
}

.gs-active-clear {
  flex-shrink: 0;
  border: none;
  background: none;
  color: var(--text-dim);
  cursor: pointer;
  padding: 0;
  display: flex;
  align-items: center;
  font-size: 1rem;
  transition: color 0.15s;
}

.gs-active-clear:hover { color: #f87171; }
</style>
