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

  // Opacidade de cada camada (base e overlay), escala 0–1
  const layerOpacity = ref(
    Object.fromEntries(
      [...Object.keys(BASE_LAYERS), ...Object.keys(OVERLAY_LAYERS)].map((k) => [k, 1]),
    ),
  )

  // Modo identificar (GetFeatureInfo) ativo por overlay
  const infoActive = ref(
    Object.fromEntries(Object.keys(OVERLAY_LAYERS).map((k) => [k, false])),
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
    if (key in layerOpacity.value) layerOpacity.value[key] = value
  }

  function toggleLayerInfo(key) {
    if (!(key in infoActive.value)) return
    const wasActive = infoActive.value[key]
    // Desativa todas as camadas (comportamento radio)
    Object.keys(infoActive.value).forEach((k) => { infoActive.value[k] = false })
    // Se não estava ativa, ativa; se já estava, permanece desativada (toggle off)
    if (!wasActive) infoActive.value[key] = true
  }

  return {
    activeBaseLayerKey,
    activeBaseLayer,
    availableBaseLayers,
    visibleOverlays,
    availableOverlays,
    layerOpacity,
    infoActive,
    setBaseLayer,
    toggleOverlay,
    setLayerOpacity,
    toggleLayerInfo,
  }
})
