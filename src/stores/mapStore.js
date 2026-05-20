// src/stores/mapStore.js
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { BASE_LAYERS, OVERLAY_LAYERS } from '@/config/layers'

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

  // ── Getters ─────────────────────────────────────────────────────────────────

  const activeBaseLayer = computed(() => BASE_LAYERS[activeBaseLayerKey.value])

  const availableBaseLayers = computed(() =>
    Object.entries(BASE_LAYERS).map(([key, { label, meta }]) => ({ key, label, meta })),
  )

  const availableOverlays = computed(() =>
    Object.entries(OVERLAY_LAYERS).map(([key, cfg]) => ({ key, ...cfg })),
  )

  // ── Ações ───────────────────────────────────────────────────────────────────

  function setBaseLayer(key) {
    if (BASE_LAYERS[key]) activeBaseLayerKey.value = key
  }

  function toggleOverlay(key) {
    if (key in visibleOverlays.value) visibleOverlays.value[key] = !visibleOverlays.value[key]
  }

  function setLayerOpacity(key, value) {
    // Garante que o valor recebido fique estritamente no intervalo aceitável de 0 a 1
    if (key in layerOpacity.value) {
      layerOpacity.value[key] = Math.max(0, Math.min(1, value))
    }
  }

  return {
    activeBaseLayerKey,
    activeBaseLayer,
    availableBaseLayers,
    visibleOverlays,
    availableOverlays,
    layerOpacity,
    setBaseLayer,
    toggleOverlay,
    setLayerOpacity,
  }
})