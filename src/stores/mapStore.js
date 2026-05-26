// src/stores/mapStore.js
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { BASE_LAYERS, OVERLAY_LAYERS, OVERLAY_CATEGORIES } from '@/config/layers'

export const useMapStore = defineStore('map', () => {
  // ── Estado ──────────────────────────────────────────────────────────────────

  const defaultBaseKey =
    Object.entries(BASE_LAYERS).find(([, cfg]) => cfg.active)?.[0] ??
    Object.keys(BASE_LAYERS)[0]

  const activeBaseLayerKey = ref(defaultBaseKey)

  const visibleOverlays = ref(
    Object.fromEntries(Object.entries(OVERLAY_LAYERS).map(([k, cfg]) => [k, cfg.active])),
  )

  // Opacidade de cada camada (base e overlay) inicializada dinamicamente em 1 (100%)
  const layerOpacity = ref(
    Object.fromEntries(
      [...Object.keys(BASE_LAYERS), ...Object.keys(OVERLAY_LAYERS)].map((k) => [k, 1]),
    ),
  )

  // Filtro de busca ativo por camada: { field, operator, value } | null
  const layerSearchFilters = ref(
    Object.fromEntries(Object.keys(OVERLAY_LAYERS).map((k) => [k, null])),
  )

  // Localização geoespacial buscada: { lat, lng, label } | null
  const geoLocation = ref(null)

  // ── Getters ─────────────────────────────────────────────────────────────────

  const activeBaseLayer = computed(() => BASE_LAYERS[activeBaseLayerKey.value])

  const availableBaseLayers = computed(() =>
    Object.entries(BASE_LAYERS).map(([key, { label, meta }]) => ({ key, label, meta })),
  )

  // Lista plana de overlays (retrocompatibilidade com MapContainer.vue)
  const availableOverlays = computed(() =>
    Object.entries(OVERLAY_LAYERS).map(([key, cfg]) => ({ key, ...cfg })),
  )

  // Lista de categorias enriquecida com estado reativo de visibilidade
  const availableCategories = computed(() =>
    Object.entries(OVERLAY_CATEGORIES).map(([catKey, cat]) => ({
      key: catKey,
      label: cat.label,
      color: cat.color,
      icon: cat.icon,
      layers: Object.entries(cat.layers).map(([lKey, l]) => ({
        key: lKey,
        ...l,
        visible: visibleOverlays.value[lKey] ?? false,
        opacity: layerOpacity.value[lKey] ?? 1,
      })),
    }))
  )

  // ── Ações ───────────────────────────────────────────────────────────────────

  function setBaseLayer(key) {
    if (BASE_LAYERS[key]) activeBaseLayerKey.value = key
  }

  function toggleOverlay(key) {
    if (key in visibleOverlays.value) visibleOverlays.value[key] = !visibleOverlays.value[key]
  }

  function setLayerOpacity(key, value) {
    if (key in layerOpacity.value) {
      layerOpacity.value[key] = Math.max(0, Math.min(1, value))
    }
  }

  // filter: { field: string, operator: string, value: string } | null
  function setSearchFilter(key, filter) {
    if (key in layerSearchFilters.value) {
      layerSearchFilters.value[key] = filter
    }
  }

  function clearSearchFilter(key) {
    if (key in layerSearchFilters.value) {
      layerSearchFilters.value[key] = null
    }
  }

  function setGeoLocation(payload) {
    geoLocation.value = payload
  }

  function clearGeoLocation() {
    geoLocation.value = null
  }

  return {
    activeBaseLayerKey,
    activeBaseLayer,
    availableBaseLayers,
    visibleOverlays,
    availableOverlays,
    availableCategories,
    layerOpacity,
    layerSearchFilters,
    setBaseLayer,
    toggleOverlay,
    setLayerOpacity,
    setSearchFilter,
    clearSearchFilter,
    geoLocation,
    setGeoLocation,
    clearGeoLocation,
  }
})