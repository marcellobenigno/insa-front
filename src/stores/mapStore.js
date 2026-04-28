import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

// ─── Camadas Base ─────────────────────────────────────────────────────────────

const BASE_LAYERS = {
  osm: {
    label: 'OpenStreetMap',
    url: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
    attribution:
      '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    maxZoom: 19,
  },
  satellite: {
    label: 'Satélite (ESRI)',
    url: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
    attribution:
      'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community',
    maxZoom: 18,
  },
}

// ─── Camadas de Sobreposição (WMS) ────────────────────────────────────────────

// URL base do serviço WMS do workspace INSA
export const WMS_URL = 'http://localhost:8080/geoserver/insa/wms'

const OVERLAY_LAYERS = {
  municipios_semiarido: {
    label: 'Municípios do Semiárido',
    wmsLayer: 'insa:municipios_semiarido',
  },
  limite_semiarido: {
    label: 'Limite do Semiárido',
    wmsLayer: 'insa:limite_semiarido',
  },
}

// ─── Store ────────────────────────────────────────────────────────────────────

export const useMapStore = defineStore('map', () => {
  // ── Estado ──────────────────────────────────────────────────────────────────

  // Chave da camada base ativa
  const activeBaseLayerKey = ref('osm')

  // Visibilidade de cada camada de sobreposição (chave → boolean)
  const visibleOverlays = ref(
    Object.fromEntries(Object.keys(OVERLAY_LAYERS).map((k) => [k, true])),
  )

  // ── Getters ─────────────────────────────────────────────────────────────────

  // Configuração completa da camada base ativa
  const activeBaseLayer = computed(() => BASE_LAYERS[activeBaseLayerKey.value])

  // Lista de camadas base para montar os radio buttons
  const availableBaseLayers = computed(() =>
    Object.entries(BASE_LAYERS).map(([key, { label }]) => ({ key, label })),
  )

  // Lista de overlays com configuração WMS para montar os checkboxes
  const availableOverlays = computed(() =>
    Object.entries(OVERLAY_LAYERS).map(([key, { label, wmsLayer }]) => ({
      key,
      label,
      wmsLayer,
    })),
  )

  // ── Ações ───────────────────────────────────────────────────────────────────

  function setBaseLayer(key) {
    if (BASE_LAYERS[key]) {
      activeBaseLayerKey.value = key
    }
  }

  function toggleOverlay(key) {
    if (key in visibleOverlays.value) {
      visibleOverlays.value[key] = !visibleOverlays.value[key]
    }
  }

  return {
    activeBaseLayerKey,
    activeBaseLayer,
    availableBaseLayers,
    visibleOverlays,
    availableOverlays,
    setBaseLayer,
    toggleOverlay,
  }
})
